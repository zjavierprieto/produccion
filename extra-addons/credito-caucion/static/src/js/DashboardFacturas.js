/** @odoo-module */

// Importación de los componentes y servicios necesarios
import { registry } from "@web/core/registry";
import { TareasPendientes } from "./TareasPendientes"; // Componente para mostrar tareas pendientes
import { BarChartComponent } from "./BarChartComponent"; // Componente para gráficos de barras
import { useService } from "@web/core/utils/hooks"; // Hook para usar servicios

// Definición del componente para el dashboard de facturas en Crédito y Caución
const { Component } = owl;

export class CreditoCaucionDashboardFacturas extends Component {
    // Método setup: se ejecuta al iniciar el componente
    setup() {
        this.rpc = useService("rpc"); // Servicio para realizar llamadas RPC
        // Objeto que contiene los valores iniciales de los KPI de facturas
        this.kpiData = {
            gestor_clasificaciones: 0,
            gestor_cobros: 0,
        };
        
        this.loadKpiData(); // Llamada para cargar los datos de los KPI de facturas
    }

    // Método para cargar los datos de los KPI de facturas desde el backend mediante una llamada RPC
    async loadKpiData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw", {
                model: "riesgo", // Modelo en el backend que provee los datos
                method: "get_kpi_facturas_data", // Método del modelo que obtiene los datos específicos de facturas
                args: [],
                kwargs: {}, 
            });
            console.log('Resultado KPI Facturas:', result); // Depuración para verificar los datos obtenidos
            this.kpiData = result; // Actualización del objeto kpiData con los resultados obtenidos
            this.render(); // Renderizado del componente una vez que se obtienen los datos
        } catch (error) {
            console.error("Error KPI Facturas:", error); // Manejo de errores en la carga de los datos
        }
    }
}

// Registro del template del componente y sus subcomponentes
CreditoCaucionDashboardFacturas.template = "credito-caucion.CreditoCaucionDashboardFacturas";
CreditoCaucionDashboardFacturas.components = { TareasPendientes, BarChartComponent };

// Registro del componente en la categoría de "actions" para ser llamado en las acciones de Odoo
registry.category("actions").add("credito-caucion.dashboard_facturas", CreditoCaucionDashboardFacturas);
