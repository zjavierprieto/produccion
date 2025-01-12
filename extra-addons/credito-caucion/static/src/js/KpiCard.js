/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class KpiCard extends Component {
    setup() {
        this.actionService = useService("action");
    }

    onClick() {
        let actionId;
        switch (this.props.name) {
            case 'AFP':
                actionId = "credito-caucion.action_afp";
                break;
            case 'Prórrogas':
                actionId = "credito-caucion.action_prorroga"; 
                break;
            case 'Siniestros':
                actionId = "credito-caucion.action_siniestro"; 
                break;
            case 'Clasificaciones':
                actionId = "credito-caucion.action_clasificacion"; 
                break;
            default:
                console.error("Unknown action type:", this.props.name);
                return;
        }

        // Invoca la acción basada en el tipo
        this.actionService.doAction(actionId, {
            additional_context: {
                // Puedes pasar contexto adicional si es necesario
            }
        });
    }
}

KpiCard.template = "credito-caucion.KpiCard";
