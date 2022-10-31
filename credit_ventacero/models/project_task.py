# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'


    @api.model
    def create(self, vals):
        result = super(ProjectTask, self).create(vals)
        
        if result.project_id:
            result.description = result.project_id.description

        return result