from odoo import models, fields, api

class CreditNoteReasons(models.Model):
    _name ='credit.note.reasons'
    _description = 'Motivos de nota de credito'  
    
    name = fields.Char(string="Nombre")


  
  




   