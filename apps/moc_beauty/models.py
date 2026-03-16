from django.db import models
from django.conf import settings

# Create your models here.


class MBRole(models.Model):
    code = models.CharField(max_length=30, unique=True)  # ADMIN, EMPLEADO, CLIENTE
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class MBMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mb_memberships")
    role = models.ForeignKey(MBRole, on_delete=models.PROTECT)

    # opcional: campos extra por rol/relación
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user.username} -> {self.role.code}"
    


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client_id = models.AutoField(primary_key=True)
    acepta_marketing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name

class Empleado(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    empleado_id = models.AutoField(primary_key=True)
    puesto = models.CharField(max_length=100)

    def __str__(self):
        return self.user.name
    
class EstadoServicio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    estado_actual = models.ForeignKey(
        "EstadoServicio",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre

class ServicioEstado(models.Model):
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="estados"
    )
    estado = models.ForeignKey(
        "EstadoServicio",
        on_delete=models.PROTECT
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_cambio"]


    
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre
    

    
class VentaDetalle(models.Model):
    venta = models.ForeignKey("Venta", on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        if self.servicio is not None:
            return f"Detalle of {self.servicio.nombre } in sale {self.venta.id}"
        elif self.producto is not None:
            return f"Detalle of {self.producto.nombre } in sale {self.venta.id}"
        else:
            return f"Detalle in sale {self.venta.id}"

class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id} for {self.cliente.user.name} on {self.fecha.date}"

        

class Sala(models.Model):
    numero = models.IntegerField(primary_key=True)
    servicios = models.ManyToManyField(Servicio, blank=True, related_name='salas')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)


    def __str__(self):
        return f"Sala {self.numero}"


class Cita(models.Model):
    cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cita for {self.cliente.user.name} on {self.fecha.date} at {self.fecha.time}"