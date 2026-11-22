class SoftwareFJError(Exception):
    def __init__(self, mensaje, codigo_error="ERR-000"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self):
        return f"[{self.codigo_error}] {self.mensaje}"


class ValidacionDatosError(SoftwareFJError):
    def __init__(self, mensaje, campo="desconocido"):
        super().__init__(f"Error de validacion en '{campo}': {mensaje}", "ERR-VAL-101")
        self.campo = campo


class ParametroFaltanteError(SoftwareFJError):
    def __init__(self, parametro):
        super().__init__(f"Falta el parametro obligatorio: '{parametro}'.", "ERR-PAR-102")
        self.parametro = parametro


class ServicioNoDisponibleError(SoftwareFJError):
    def __init__(self, nombre_servicio):
        super().__init__(
            f"El servicio '{nombre_servicio}' no esta disponible actualmente.",
            "ERR-SRV-201",
        )
        self.nombre_servicio = nombre_servicio


class ReservaInvalidaError(SoftwareFJError):
    def __init__(self, mensaje):
        super().__init__(f"Operacion de reserva invalida: {mensaje}", "ERR-RES-301")


class OperacionNoPermitidaError(SoftwareFJError):
    def __init__(self, mensaje):
        super().__init__(f"Operacion no permitida: {mensaje}", "ERR-OP-401")


class CalculoCostoError(SoftwareFJError):
    def __init__(self, mensaje):
        super().__init__(f"Error en el calculo de costos: {mensaje}", "ERR-CAL-501")
