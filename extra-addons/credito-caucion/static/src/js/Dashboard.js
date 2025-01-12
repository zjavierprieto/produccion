/** @odoo-module */

// Importación de los componentes y servicios necesarios
import { registry } from "@web/core/registry";
import { KpiCard } from "./KpiCard"; // Componente personalizado para mostrar KPIs
import { TareasPendientes } from "./TareasPendientes"; // Componente para mostrar tareas pendientes
import { BarChartComponent } from "./BarChartComponent"; // Componente para gráficos de barras
import { LineChartComponent } from "./LineChartComponent"; // Componente para gráficos de líneas
import { useService } from "@web/core/utils/hooks"; // Hook para usar servicios

// Definición del componente principal del dashboard de Crédito y Caución
const { Component } = owl;

export class CreditoCaucionDashboard extends Component {
    // Método setup: se ejecuta al iniciar el componente
    setup() {
        this.rpc = useService("rpc"); // Servicio para realizar llamadas RPC
        // Objeto que contiene los valores iniciales de los KPI a mostrar
        this.kpiData = {
            clasificaciones: 0,
            clasificaciones_importe: 0,
            afp: 0,
            afp_importe: 0,
            prorrogas: 0,
            prorrogas_importe: 0,
            siniestros: 0,
            siniestros_importe: 0,
            alertas: 0,
            actividades: 0,
        };
        
        this.loadKpiData(); // Llamada para cargar los datos de los KPI
    }

    // Método para cargar los datos de los KPI desde el backend mediante una llamada RPC
    async loadKpiData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw", {
                model: "riesgo", // Modelo en el backend que provee los datos
                method: "get_kpi_data", // Método del modelo que obtiene los datos
                args: [],
                kwargs: {}, 
            });
            this.kpiData = result; // Actualización del objeto kpiData con los resultados obtenidos
            this.render(); // Renderizado del componente una vez que se obtienen los datos
        } catch (error) {
            console.error("Error KPI General:", error); // Manejo de errores en la carga de los datos
        }
    }
}

// Registro del template del componente y sus subcomponentes
CreditoCaucionDashboard.template = "credito-caucion.CreditoCaucionDashboard";
CreditoCaucionDashboard.components = { KpiCard, BarChartComponent, LineChartComponent, TareasPendientes };

// Registro del componente en la categoría de "actions" para ser llamado en las acciones de Odoo
registry.category("actions").add("credito-caucion.dashboard", CreditoCaucionDashboard);
