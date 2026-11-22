import logging
from excepciones import SoftwareFJError, ValidacionDatosError, ReservaInvalidaError
from modelos import Cliente, Servicio, Reserva


def configurar_logger(ruta_log="software_fj.log"):
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        archivo_handler = logging.FileHandler(ruta_log, mode="w", encoding="utf-8")
        archivo_handler.setLevel(logging.DEBUG)
        archivo_handler.setFormatter(formato)
        logger.addHandler(archivo_handler)

    return logger


class SistemaGestionSoftwareFJ:
    def __init__(self, ruta_log="software_fj.log"):
        self.logger = configurar_logger(ruta_log)
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self.logger.info("=== INICIO DEL SISTEMA INTEGRAL DE GESTION SOFTWARE FJ ===")

    def registrar_cliente(self, cliente):
        try:
            if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
                raise ValidacionDatosError(
                    f"Ya existe un cliente con el ID '{cliente.id_entidad}'.",
                    "id_entidad",
                )
        except SoftwareFJError as err:
            self.logger.error(f"Fallo al registrar cliente: {err}")
            print(f"[ERROR CONTROLADO] {err}")
            return False
        else:
            self.clientes.append(cliente)
            self.logger.info(f"Cliente registrado: {cliente.obtener_resumen()}")
            print(f"[OK] {cliente.obtener_resumen()}")
            return True
        finally:
            self.logger.debug("Finalizada verificacion de registro de cliente.")

    def registrar_servicio(self, servicio):
        try:
            if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
                raise ValidacionDatosError(
                    f"Ya existe un servicio con el ID '{servicio.id_entidad}'.",
                    "id_entidad",
                )
        except SoftwareFJError as err:
            self.logger.error(f"Fallo al registrar servicio: {err}")
            print(f"[ERROR CONTROLADO] {err}")
            return False
        else:
            self.servicios.append(servicio)
            self.logger.info(f"Servicio registrado: {servicio.obtener_resumen()}")
            print(f"[OK] {servicio.obtener_resumen()}")
            return True
        finally:
            self.logger.debug("Finalizada verificacion de catalogo de servicios.")

    def crear_y_confirmar_reserva(
        self,
        id_reserva,
        cliente,
        servicio,
        duracion_horas,
        descuento_extra=0.0,
        recargo_urgencia=0.0,
        **parametros_servicio,
    ):
        try:
            if any(r.id_entidad == id_reserva for r in self.reservas):
                raise ReservaInvalidaError(f"El codigo de reserva '{id_reserva}' ya existe.")

            nueva_reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion_horas=duracion_horas,
                **parametros_servicio,
            )
            nueva_reserva.confirmar(
                descuento_extra=descuento_extra,
                recargo_urgencia=recargo_urgencia,
            )
        except SoftwareFJError as err:
            causa = f" | Causa raiz: {err.__cause__}" if err.__cause__ else ""
            self.logger.error(f"Fallo en reserva '{id_reserva}': {err}{causa}")
            print(f"[ERROR CONTROLADO] Reserva '{id_reserva}' rechazada -> {err}{causa}")
            return None
        except Exception as inesperado:
            error_encadenado = ReservaInvalidaError(f"Error inesperado en reserva '{id_reserva}'.")
            self.logger.critical(f"{error_encadenado} | Detalle: {inesperado}")
            print(f"[ERROR CRITICO CONTROLADO] {error_encadenado}")
            return None
        else:
            self.reservas.append(nueva_reserva)
            self.logger.info(f"Reserva confirmada: {nueva_reserva.obtener_resumen()}")
            print(f"[OK] {nueva_reserva.obtener_resumen()}")
            return nueva_reserva
        finally:
            self.logger.debug(f"Cierre de transaccion de reserva '{id_reserva}'.")
