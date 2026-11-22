from abc import ABC, abstractmethod
from excepciones import (
    ValidacionDatosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoCostoError,
)


class EntidadSistema(ABC):
    def __init__(self, id_entidad):
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValidacionDatosError("El identificador no puede estar vacio.", "id_entidad")
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self):
        return self._id_entidad

    @abstractmethod
    def obtener_resumen(self):
        pass


class Cliente(EntidadSistema):
    def __init__(self, id_cliente, nombre, correo, telefono, es_corporativo=False):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self._es_corporativo = bool(es_corporativo)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionDatosError("El nombre debe tener al menos 3 caracteres.", "nombre")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValidacionDatosError(f"Correo invalido: '{valor}'.", "correo")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        digitos = "".join(c for c in str(valor) if c.isdigit())
        if len(digitos) < 7:
            raise ValidacionDatosError("El telefono debe tener al menos 7 digitos.", "telefono")
        self._telefono = valor.strip()

    @property
    def es_corporativo(self):
        return self._es_corporativo

    def obtener_resumen(self):
        tipo = "Corporativo" if self._es_corporativo else "Individual"
        return f"Cliente [{self.id_entidad}] {self._nombre} ({tipo}) - {self._correo}"


class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre, tarifa_base_hora, disponible=True):
        super().__init__(id_servicio)
        if not nombre or not nombre.strip():
            raise ValidacionDatosError("El nombre del servicio es obligatorio.", "nombre")
        if not isinstance(tarifa_base_hora, (int, float)) or tarifa_base_hora <= 0:
            raise ValidacionDatosError("La tarifa base por hora debe ser mayor que cero.", "tarifa_base_hora")
        self._nombre = nombre.strip()
        self._tarifa_base_hora = float(tarifa_base_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base_hora(self):
        return self._tarifa_base_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, estado):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, horas, **kwargs):
        pass

    @abstractmethod
    def calcular_costo_base(self, horas, **kwargs):
        pass

    def calcular_costo(self, horas, descuento_pct=0.0, iva_pct=0.19, recargo_urgencia=0.0, **kwargs):
        try:
            self.validar_parametros(horas, **kwargs)
            if descuento_pct < 0 or descuento_pct >= 1:
                raise ValidacionDatosError("El descuento debe estar entre 0.0 y 0.99.", "descuento_pct")
            if iva_pct < 0:
                raise ValidacionDatosError("El IVA no puede ser negativo.", "iva_pct")
            if recargo_urgencia < 0:
                raise ValidacionDatosError("El recargo no puede ser negativo.", "recargo_urgencia")
            subtotal = self.calcular_costo_base(horas, **kwargs)
            subtotal_desc = subtotal * (1 - descuento_pct)
            total = (subtotal_desc + recargo_urgencia) * (1 + iva_pct)
            return round(total, 2)
        except ValidacionDatosError as err:
            raise CalculoCostoError(f"No se pudo calcular el costo de '{self._nombre}'.") from err

    def obtener_resumen(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio [{self.id_entidad}] {self._nombre} | Tarifa: ${self._tarifa_base_hora:,.2f}/h | {estado}"


class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_base_hora, capacidad_maxima, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0:
            raise ValidacionDatosError("La capacidad maxima debe ser positiva.", "capacidad_maxima")
        self._capacidad_maxima = capacidad_maxima

    def validar_parametros(self, horas, **kwargs):
        if horas <= 0 or horas > 12:
            raise ValidacionDatosError("La sala se reserva entre 1 y 12 horas.", "horas")
        asistentes = kwargs.get("asistentes")
        if asistentes is None:
            raise ParametroFaltanteError("asistentes")
        if asistentes <= 0 or asistentes > self._capacidad_maxima:
            raise ValidacionDatosError(
                f"Asistentes ({asistentes}) fuera de rango (1 a {self._capacidad_maxima}).",
                "asistentes",
            )

    def calcular_costo_base(self, horas, **kwargs):
        asistentes = kwargs.get("asistentes", 1)
        factor = 1.15 if asistentes > (self._capacidad_maxima * 0.8) else 1.0
        return self._tarifa_base_hora * horas * factor


class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_base_hora, stock_disponible, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise ValidacionDatosError("El stock debe ser mayor o igual a 0.", "stock_disponible")
        self._stock_disponible = stock_disponible

    def validar_parametros(self, horas, **kwargs):
        if horas < 2:
            raise ValidacionDatosError("El alquiler minimo es de 2 horas.", "horas")
        cantidad = kwargs.get("cantidad")
        if cantidad is None:
            raise ParametroFaltanteError("cantidad")
        if cantidad <= 0 or cantidad > self._stock_disponible:
            raise ValidacionDatosError(
                f"Cantidad ({cantidad}) supera el stock ({self._stock_disponible}).",
                "cantidad",
            )

    def calcular_costo_base(self, horas, **kwargs):
        cantidad = kwargs.get("cantidad", 1)
        seguro = 15000.0 * cantidad
        return (self._tarifa_base_hora * horas * cantidad) + seguro


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_base_hora, especialidad, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not especialidad or not especialidad.strip():
            raise ValidacionDatosError("La especialidad es obligatoria.", "especialidad")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, horas, **kwargs):
        if horas < 1 or horas > 40:
            raise ValidacionDatosError("La asesoria debe durar entre 1 y 40 horas.", "horas")
        nivel = kwargs.get("nivel", "semi-senior").lower()
        if nivel not in ("junior", "semi-senior", "senior"):
            raise ValidacionDatosError(f"Nivel invalido: '{nivel}'.", "nivel")

    def calcular_costo_base(self, horas, **kwargs):
        nivel = kwargs.get("nivel", "semi-senior").lower()
        mult = {"junior": 0.85, "semi-senior": 1.0, "senior": 1.35}
        return self._tarifa_base_hora * horas * mult[nivel]


class Reserva(EntidadSistema):
    def __init__(self, id_reserva, cliente, servicio, duracion_horas, **parametros_servicio):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ValidacionDatosError("Cliente invalido.", "cliente")
        if not isinstance(servicio, Servicio):
            raise ValidacionDatosError("Servicio invalido.", "servicio")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(servicio.nombre)
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ReservaInvalidaError("La duracion debe ser mayor a 0 horas.")
        servicio.validar_parametros(duracion_horas, **parametros_servicio)
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = float(duracion_horas)
        self._parametros_servicio = parametros_servicio
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self, descuento_extra=0.0, recargo_urgencia=0.0):
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar en estado {self._estado}.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(self._servicio.nombre)
        desc_corp = 0.10 if self._cliente.es_corporativo else 0.0
        desc_total = min(desc_corp + descuento_extra, 0.50)
        self._costo_total = self._servicio.calcular_costo(
            horas=self._duracion_horas,
            descuento_pct=desc_total,
            recargo_urgencia=recargo_urgencia,
            **self._parametros_servicio,
        )
        self._estado = "CONFIRMADA"
        return self._costo_total

    def cancelar(self, motivo="Solicitado por el cliente"):
        if self._estado == "PROCESADA":
            raise OperacionNoPermitidaError("No se puede cancelar una reserva PROCESADA.")
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya esta CANCELADA.")
        self._estado = "CANCELADA"

    def procesar(self):
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(f"Debe estar CONFIRMADA para procesarse ({self._estado}).")
        self._estado = "PROCESADA"
        return f"Reserva {self.id_entidad} procesada para {self._cliente.nombre} | Total: ${self._costo_total:,.2f}"

    def obtener_resumen(self):
        return (
            f"Reserva [{self.id_entidad}] Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Estado: {self._estado} | Total: ${self._costo_total:,.2f}"
        )
