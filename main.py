from excepciones import SoftwareFJError
from modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestor import SistemaGestionSoftwareFJ


def ejecutar_simulacion():
    print("=================================================================")
    print("  SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ (SIMULACION FASE 4) ")
    print("=================================================================\n")

    sistema = SistemaGestionSoftwareFJ("software_fj.log")

    # Operacion 1 (Valida): Registro de cliente corporativo
    c1 = Cliente("CLI-001", "TecnoAndes S.A.S.", "contacto@tecnoandes.co", "3104567890", es_corporativo=True)
    sistema.registrar_cliente(c1)

    # Operacion 2 (Valida): Registro de cliente individual
    c2 = Cliente("CLI-002", "Larieth Salazar Leon", "larieth.salazar@correo.com", "3159876543", es_corporativo=False)
    sistema.registrar_cliente(c2)

    # Operacion 3 (Invalida): Cliente con correo y telefono invalidos
    try:
        c_invalido = Cliente("CLI-003", "Carlos Perez", "correo-sin-arroba", "123")
        sistema.registrar_cliente(c_invalido)
    except SoftwareFJError as err:
        sistema.logger.warning(f"Captura en creacion de cliente: {err}")
        print(f"[EXCEPCION CAPTURADA] {err}")

    # Operacion 4 (Invalida): Cliente con ID duplicado
    c_duplicado = Cliente("CLI-001", "Otra Empresa S.A.", "info@otraempresa.com", "3001112233")
    sistema.registrar_cliente(c_duplicado)

    # Operacion 5 (Valida): Registro de servicios especializados
    s_sala = ReservaSala("SRV-01", "Sala Innovacion Ejecutiva", 80000.0, capacidad_maxima=20, disponible=True)
    s_equipo = AlquilerEquipo("SRV-02", "Workstation GPU NVIDIA", 45000.0, stock_disponible=5, disponible=True)
    s_asesoria = AsesoriaEspecializada("SRV-03", "Arquitectura Cloud y Python", 120000.0, especialidad="Cloud", disponible=True)
    s_inactiva = ReservaSala("SRV-04", "Sala Auditorio Norte", 150000.0, capacidad_maxima=50, disponible=False)

    sistema.registrar_servicio(s_sala)
    sistema.registrar_servicio(s_equipo)
    sistema.registrar_servicio(s_asesoria)
    sistema.registrar_servicio(s_inactiva)

    # Operacion 6 (Invalida): Servicio con tarifa negativa
    try:
        s_erroneo = AlquilerEquipo("SRV-99", "Servidor Defectuoso", -25000.0, stock_disponible=2)
        sistema.registrar_servicio(s_erroneo)
    except SoftwareFJError as err:
        sistema.logger.warning(f"Captura en creacion de servicio: {err}")
        print(f"[EXCEPCION CAPTURADA] {err}")

    # Operacion 7 (Valida): Reserva de sala con descuento corporativo
    res1 = sistema.crear_y_confirmar_reserva("RES-101", c1, s_sala, duracion_horas=4, asistentes=18)

    # Operacion 8 (Valida): Reserva de alquiler de equipos
    res2 = sistema.crear_y_confirmar_reserva("RES-102", c2, s_equipo, duracion_horas=5, cantidad=2)

    # Operacion 9 (Invalida): Reserva sobre servicio no disponible
    sistema.crear_y_confirmar_reserva("RES-103", c1, s_inactiva, duracion_horas=3, asistentes=25)

    # Operacion 10 (Invalida): Reserva sin parametro obligatorio (cantidad)
    sistema.crear_y_confirmar_reserva("RES-104", c2, s_equipo, duracion_horas=3)

    # Operacion 11 (Invalida): Reserva con exceso de asistentes en sala
    sistema.crear_y_confirmar_reserva("RES-105", c1, s_sala, duracion_horas=2, asistentes=45)

    # Operacion 12 (Valida e Invalida): Procesar reserva y luego intentar cancelarla
    try:
        if res1:
            msg = res1.procesar()
            sistema.logger.info(msg)
            print(f"[OK] {msg}")
            res1.cancelar("Cambio de agenda")
    except SoftwareFJError as err:
        sistema.logger.error(f"Error controlado en estado de reserva: {err}")
        print(f"[ERROR CONTROLADO] {err}")

    if res2:
        res2.cancelar("Reprogramacion solicitada")
        sistema.logger.info(f"Reserva cancelada: {res2.obtener_resumen()}")
        print(f"[OK] {res2.obtener_resumen()}")

    sistema.logger.info("=== FIN DE LA SIMULACION: SISTEMA ESTABLE ===")
    print("\n=================================================================")
    print("  SIMULACION FINALIZADA CON EXITO                                ")
    print("=================================================================")


if __name__ == "__main__":
    ejecutar_simulacion()
