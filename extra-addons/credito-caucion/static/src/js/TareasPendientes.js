/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TareasPendientes extends Component {
    setup() {
        this.actionService = useService("action");
    }

    onClick() {
        let actionId;
        switch (this.props.name) {
            case 'Alertas':
                actionId = "credito-caucion.action_alerta";
                break;
            case 'Actividades':
                actionId = "credito-caucion.action_riesgo_activity"; 
                break;
            case 'Clasificaciones a Gestionar':
                actionId = "credito-caucion.action_gestor_clasificacion"; 
                break;
            case 'Cobros a Gestionar':
                actionId = "credito-caucion.action_gestor_cobros"; 
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

TareasPendientes.template = "credito-caucion.TareasPendientes";
