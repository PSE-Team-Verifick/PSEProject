import copy

from onnx import ModelProto, TensorProto, NodeProto, numpy_helper
import onnx


class NetworkModifier:
    @staticmethod
    def _expected_numel(initializer: TensorProto) -> int:
        numel = 1
        for dim in initializer.dims:
            numel *= int(dim)
        return max(numel, 0)

    @staticmethod
    def _clear_tensor_payload(initializer: TensorProto) -> None:
        for field_name in (
            "float_data",
            "int32_data",
            "int64_data",
            "string_data",
            "double_data",
            "uint64_data",
        ):
            field = getattr(initializer, field_name, None)
            if field is not None:
                del field[:]
        if initializer.HasField("raw_data"):
            initializer.ClearField("raw_data")
        if initializer.HasField("segment"):
            initializer.ClearField("segment")
        if len(initializer.external_data) > 0:
            initializer.ClearField("external_data")
        initializer.data_location = TensorProto.DEFAULT

    @staticmethod
    def _materialize_float_initializer(initializer: TensorProto) -> None:
        if initializer.data_type != TensorProto.FLOAT:
            return
        try:
            values = numpy_helper.to_array(initializer).astype("float32").reshape(-1).tolist()
        except Exception:
            if len(initializer.float_data) > 0:
                values = list(initializer.float_data)
            else:
                numel = 1
                for dim in initializer.dims:
                    numel *= int(dim)
                values = [0.0] * max(numel, 0)
        NetworkModifier._clear_tensor_payload(initializer)
        initializer.float_data.extend(values)

    @staticmethod
    def _ensure_float_initializer_size(initializer: TensorProto) -> None:
        if initializer.data_type != TensorProto.FLOAT:
            return
        expected = NetworkModifier._expected_numel(initializer)
        current = len(initializer.float_data)
        if current < expected:
            initializer.float_data.extend([0.0] * (expected - current))
        elif current > expected:
            del initializer.float_data[expected:]

    @staticmethod
    def _repair_float_initializers(model: ModelProto) -> None:
        for initializer in model.graph.initializer:
            if initializer.data_type != TensorProto.FLOAT:
                continue
            NetworkModifier._materialize_float_initializer(initializer)
            NetworkModifier._ensure_float_initializer_size(initializer)

    @staticmethod
    def with_all_outputs(
        static_model: ModelProto,
        sampling_mode: str = "pre_activation_after_bias",
    ) -> ModelProto:
        model = copy.deepcopy(static_model)
        existing = {output.name for output in model.graph.output}
        activation_ops = {
            "Relu",
            "Sigmoid",
            "Tanh",
            "Softmax",
            "LogSoftmax",
            "LeakyRelu",
            "Elu",
            "Gelu",
            "Clip",
            "HardSigmoid",
            "HardSwish",
            "PRelu",
            "Selu",
            "Celu",
            "Mish",
            "Softplus",
            "Softsign",
            "Swish",
        }
        for node in model.graph.node:
            if node.op_type not in activation_ops:
                continue
            names: list[str] = []
            if sampling_mode == "pre_activation_after_bias":
                if node.input and node.input[0]:
                    names.append(node.input[0])  # pre-activation after bias
            elif sampling_mode == "post_activation":
                if node.output and node.output[0]:
                    names.append(node.output[0])  # post-activation
            else:
                raise ValueError(f"Invalid sampling_mode: {sampling_mode}")
            for name in names:
                if not name or name in existing:
                    continue
                vi = onnx.ValueInfoProto()
                vi.name = name
                model.graph.output.append(vi)
                existing.add(name)
        return model

    def custom_output_layer(self, static_model: ModelProto, neurons: list[tuple[int, int]], directions: list[tuple[float, float]]) -> ModelProto:
        '''

        :param static_model: the whole network, which is not changed in this function
        :param neurons: List of neurons, that should be used for the calculation
        :param directions: List of directions, that represent linear combinations of neurons
        :return: the new model
        '''
        model = copy.deepcopy(static_model)     #deepcopies so the original model does not change
        model.graph.node[model.graph.node.__len__() - 1].output.remove("output")
        model.graph.node[model.graph.node.__len__() - 1].output.append("old_output")    #redirects the old output layer
        initializers = NetworkModifier.create_initalizers(self, model, neurons, directions)
        model.graph.initializer.append(initializers[0])
        model.graph.initializer.append(initializers[1])     # adds the new initializers
        new_node = NetworkModifier.create_new_layer(self, model, neurons, initializers)
        model.graph.node.append(new_node)   # adds the new node
        model = NetworkModifier.add_bridge_neurons(self, model, neurons, directions)
        NetworkModifier._repair_float_initializers(model)
        model.graph.output[0].type.tensor_type.shape.dim[1].dim_value =  directions.__len__()       #modifies the output dim, so it matches with the initializers
        return model

    def add_bridge_neurons(self, model: ModelProto, neurons: list[tuple[int, int]], directions: list[tuple[float, float]]) -> ModelProto:
        '''

        :param model: the whole network
        :param neurons: List of neurons, that should be used for the calculation
        :param directions: List of directions, that represent linear combinations of neurons
        :return: the modified model
        '''
        for neuron in neurons:
            for layer in range(2 * neuron[0], model.graph.initializer.__len__() - 1):   # goes through all layers following
                                                                                        # the layer with the neuron in it and adds a new neuron for each layer
                initializer = model.graph.initializer[layer]
                if initializer.data_type != TensorProto.FLOAT:
                    continue
                NetworkModifier._materialize_float_initializer(initializer)
                if layer != 2 * neuron[0]:
                    initializer.dims[0] += 1
                if initializer.dims.__len__() == 2 and layer != model.graph.initializer.__len__() - 2:
                    initializer.dims[1] += 1
                    if layer == 2 * neuron[0]:
                        for node in range(0, initializer.dims[0]):
                            if node == neuron[1]:
                                initializer.float_data.insert(                       # adds the connections between the new neurons
                                    (node + 1) * initializer.dims[1] - 1, 1)
                            else:
                                initializer.float_data.insert(                       # adds the connections between old and new neurons
                                    (node + 1) * initializer.dims[1] - 1, 0)
                    else:
                        for node in range(1, initializer.dims[0] - 1):
                            initializer.float_data.insert(               # adds the connections to the new neurons
                                node * initializer.dims[1] - 1, 0)
                        initializer.float_data.append(0)
                        for node in range(1, initializer.dims[1]):
                            initializer.float_data.append(0)
                        initializer.float_data.append(1)
                else:
                    if layer != model.graph.initializer.__len__() - 2:
                        initializer.float_data.append(0)
                NetworkModifier._ensure_float_initializer_size(initializer)
        for neuron_ind in range(0, neurons.__len__()): # changes the last initializer to match the output
            for direction in directions:
                model.graph.initializer[model.graph.initializer.__len__() - 2].float_data.append(direction[neuron_ind])
        NetworkModifier._ensure_float_initializer_size(model.graph.initializer[model.graph.initializer.__len__() - 2])
        return model

    def create_initalizers(self, model: ModelProto, neurons: list[tuple[int, int]], directions: list[tuple[float, float]]) -> tuple[TensorProto, TensorProto]:
        '''

        :param model: the whole network
        :param neurons: List of neurons, that should be used for the calculation
        :param directions: List of directions, that represent linear combinations of neurons
        :return: returns the new initializers for the new output layer
        '''
        float_template = next((init for init in model.graph.initializer if init.data_type == TensorProto.FLOAT), None)
        if float_template is None:
            raise RuntimeError("Model has no FLOAT initializer to build custom output layer.")
        new_initializer1 = copy.deepcopy(float_template)
        new_initializer2 = copy.deepcopy(float_template)
        new_initializer1.name = "output_initializer_W"
        new_initializer2.name = "output_initializer_B"
        NetworkModifier._clear_tensor_payload(new_initializer1)
        NetworkModifier._clear_tensor_payload(new_initializer2)
        del new_initializer1.dims[:]
        del new_initializer2.dims[:]
        # creates the 2 new initalizers, without data
        new_initializer1.dims.append(model.graph.initializer[model.graph.initializer.__len__() - 1].dims[0])
        new_initializer1.dims.append(directions.__len__())
        new_initializer2.dims.append(directions.__len__())
        for i in range(new_initializer1.dims[0] * new_initializer1.dims[1]):    #adds data, so that dims matches the number of elements
            new_initializer1.float_data.append(0)
        for i in range(new_initializer2.dims[0]):
            new_initializer2.float_data.append(0)
        return new_initializer1, new_initializer2

    def create_new_layer(self, model: ModelProto, neurons: list[tuple[int, int]], initializers: tuple[TensorProto, TensorProto]) -> NodeProto:
        '''
        :param model: the whole network
        :param neurons: List of neurons, that should be used for the calculation
        :param initializers: the initializers for the new output layer
        :return: the new output layer
        '''
        return onnx.helper.make_node(
            "Gemm",
            [
                model.graph.node[model.graph.node.__len__() - 1].output[0],
                initializers[0].name,
                initializers[1].name,
            ],
            ["output"],
            name="new_output",
            alpha=1.0,
            beta=1.0,
            transB=0,
        )
