import models


def registrar_actividad(
    db,
    tipo,
    accion,
    titulo,
    descripcion=None,
    referencia_id=None,
    usuario="Sistema"
):

    actividad = models.ActividadSistema(

        tipo=tipo,

        accion=accion,

        titulo=titulo,

        descripcion=descripcion,

        referencia_id=referencia_id,

        usuario=usuario

    )

    db.add(actividad)