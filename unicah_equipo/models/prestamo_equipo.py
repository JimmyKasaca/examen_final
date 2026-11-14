from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UnicahPrestamoEquipo(models.Model):
    _name = "unicah.prestamo.equipo"
    _description = "Préstamo de Equipo Audiovisual"

    name = fields.Char(string="Código / Equipo", required=True)
    solicitante_id = fields.Many2one("res.partner", string="Solicitante", required=True)
    aula = fields.Char(string="Aula o Laboratorio", required=True)
    fecha_prestamo = fields.Date(string="Fecha de entrega", default=fields.Date.context_today, required=True)
    fecha_devolucion = fields.Date(string="Fecha de devolución", required=True)
    estado = fields.Selection([
        ("prestado", "Prestado"),
        ("devuelto", "Devuelto"),
    ], string="Estado", default="prestado")
    dias_prestamo = fields.Integer(string="Días de préstamo", compute="_compute_dias_prestamo", store=True)

    @api.depends("fecha_prestamo", "fecha_devolucion")
    def _compute_dias_prestamo(self):
        for rec in self:
            if rec.fecha_prestamo and rec.fecha_devolucion:
                rec.dias_prestamo = (rec.fecha_devolucion - rec.fecha_prestamo).days + 1
            else:
                rec.dias_prestamo = 0

    @api.constrains("fecha_prestamo", "fecha_devolucion")
    def _check_fechas(self):
        for rec in self:
            if rec.fecha_devolucion < rec.fecha_prestamo:
                raise ValidationError("La fecha de devolución no puede ser anterior a la fecha de entrega.")


class ResPartnerEquipo(models.Model):
    _inherit = "res.partner"

    prestamo_equipo_ids = fields.One2many("unicah.prestamo.equipo", "solicitante_id", string="Préstamos de equipo")
    total_prestamos = fields.Integer(string="Préstamos activos", compute="_compute_total_prestamos")

    @api.depends("prestamo_equipo_ids.estado")
    def _compute_total_prestamos(self):
        for partner in self:
            partner.total_prestamos = len(partner.prestamo_equipo_ids.filtered(lambda p: p.estado == "prestado"))
