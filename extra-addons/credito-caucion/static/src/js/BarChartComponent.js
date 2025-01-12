/** @odoo-module */

// Importación de componentes y hooks necesarios
import { Component } from "@odoo/owl";
import { loadJS } from "@web/core/assets"; // Para cargar scripts de manera dinámica
import { useRef, onMounted, onWillStart } from "@odoo/owl"; // Hooks de OWL

// Definición del componente de gráficos de barras
export class BarChartComponent extends Component {
    // Método setup: se ejecuta al iniciar el componente
    setup() {
        this.canvasRef = useRef("chart"); // Referencia al canvas donde se dibuja el gráfico

        // Cargar dinámicamente el script de Chart.js si no está cargado ya
        onWillStart(async () => {
            if (!window.Chart) {
                await this.loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
            }
        });

        // Renderizar el gráfico una vez que el componente esté montado
        onMounted(() => this.renderChart());
    }

    // Método para cargar dinámicamente un archivo JS (Chart.js en este caso)
    async loadJS(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script); // Añadir el script al DOM
        });
    }

    // Método para renderizar el gráfico una vez que el componente esté montado
    async renderChart() {
        if (!this.canvasRef.el) return; // Verificar que el canvas esté disponible

        const ctx = this.canvasRef.el.getContext("2d"); // Obtener el contexto del canvas
        const chartPurpose = this.props.chartPurpose; // Obtener el propósito del gráfico desde las props
        const { data, options } = await this.getChartConfig(chartPurpose); // Obtener la configuración del gráfico

        // Depuración: Imprimir datos y opciones en la consola
        console.log('Chart Data:', data);
        console.log('Chart Options:', options);

        // Destruir el gráfico anterior si existe para evitar duplicados
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        // Crear una nueva instancia del gráfico de barras usando Chart.js
        this.chartInstance = new Chart(ctx, {
            type: 'bar', // Tipo de gráfico: barra
            data: data,  // Datos a mostrar en el gráfico
            options: options,  // Opciones de configuración del gráfico
        });
    }

    // Método para obtener la configuración de los datos y opciones del gráfico según el propósito
    async getChartConfig(chartPurpose) {
        let data, options;

        // Configuración de datos y opciones según el propósito del gráfico
        switch (chartPurpose) {
            case 'distribucion_importe_clasificado':  // Propósito de distribución de importes clasificados
                try {
                    // Llamada al controlador backend para obtener los datos de distribución de importes
                    const response = await fetch('/riesgo/clasificacion_distribucion', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });

                    const result = await response.json(); // Parsear la respuesta
                    console.log('Respuesta Distribución Clasificaciones:', result);

                    // Configurar los datos del gráfico
                    data = {
                        labels: ['<6K', '6-12K', '12-20K', '20-30K', '30-50K', 
                                '50-100K', '100-250K', '250-500K', '500K-1M', '>1M'], // Rangos de importe
                        datasets: [{
                            label: '', // Etiqueta del dataset
                            data: result.result.data.map(d => d.total_importe),  // Mapeo de los importes
                            backgroundColor: 'grey' // Color de las barras
                        }]
                    };
                    
                    // Opciones para el gráfico de barras
                    options = {
                        responsive: true,
                        scales: {
                            x: {
                                beginAtZero: true,
                                offset: true,
                            },
                            y: {
                                beginAtZero: true,
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    // Modificación de las etiquetas del tooltip para incluir importes y porcentaje
                                    label: function(context) {
                                        let index = context.dataIndex;
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        let totalImporte = result.result.data[index].total_importe;
                                        let porcentaje = result.result.data[index].porcentaje;
                                        label += `${totalImporte} € (${porcentaje}%)`;
                                        return label;
                                    }
                                }
                            },
                            legend: {
                                display: false,  // No mostrar leyenda
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error); // Manejo de errores en la carga de datos
                }
                break;

            case 'ventas':  // Propósito de ventas y cobros
                try {
                    // Llamada al backend para obtener datos de ventas y cobros
                    const response = await fetch('/vencimientos/ventas_cobros', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });
            
                    const result = await response.json(); // Parsear la respuesta
                    console.log('Respuesta Ventas:', result);
            
                    // Configurar los datos del gráfico de ventas y cobros
                    data = {
                        labels: result.result.labels,  // Etiquetas de los meses
                        datasets: [
                            {
                                label: 'Facturas',
                                data: result.result.facturacion,  // Datos de facturación
                                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                yAxisID: 'y',
                                type: 'bar' // Gráfico de barras para facturas
                            },
                            {
                                label: 'Cobros',
                                data: result.result.cobros,  // Datos de cobros
                                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                yAxisID: 'y',
                                type: 'bar' // Gráfico de barras para cobros
                            },
                            {
                                label: 'Saldo facturas',
                                data: result.result.saldo_vencimientos,  // Datos de saldo de facturas
                                borderColor: '#4B4B4B',
                                backgroundColor: 'rgba(0, 0, 0, 0)',
                                type: 'line',  // Gráfico de líneas para el saldo
                                tension: 0.5
                            },
                            {
                                label: 'Deuda fuera de plazo',
                                data: result.result.deuda_fuera_plazo,  // Datos de deuda fuera de plazo
                                borderColor: 'red',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                type: 'line',  // Gráfico de líneas para la deuda fuera de plazo
                                tension: 0.5 
                            }
                        ]
                    };
            
                    // Opciones del gráfico de ventas y cobros
                    options = {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                position: 'left',
                            },
                        },
                        plugins: {
                            legend: {position: 'top'},
                            tooltip: {
                                callbacks: {
                                    // Personalización de las etiquetas del tooltip
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('es-ES').format(context.parsed.y) + ' €';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error); // Manejo de errores en la carga de datos
                }
                break;

            case 'saldo_facturas':  // Propósito de mostrar el saldo de las facturas
                try {
                    // Llamada al backend para obtener los datos del saldo de facturas
                    const response = await fetch('/vencimientos/saldo_facturas', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });
            
                    const result = await response.json(); // Parsear la respuesta
                    console.log('Respuesta Saldo Facturas:', result);
            
                    // Configurar los datos del gráfico de saldo de facturas
                    data = {
                        labels: result.result.labels,  // Etiquetas obtenidas del backend
                        datasets: [{
                            label: 'Saldo Facturas',
                            data: result.result.datasets,  // Datos obtenidos del backend
                            backgroundColor: 'rgba(255, 206, 86, 0.5)',
                            borderColor: 'rgba(255, 206, 86, 1)'
                        }]
                    };
            
                    // Opciones del gráfico de saldo de facturas
                    options = {
                        responsive: true,
                        scales: {
                            x: {beginAtZero: true},
                            y: {beginAtZero: true}
                        },
                        plugins: {
                            legend: {display: false}, // Ocultar leyenda
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('es-ES').format(context.parsed.y) + ' €';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error); // Manejo de errores en la carga de datos
                }
                break;
            
            case 'proximos_cobros_previstos':  // Propósito de mostrar los próximos cobros previstos
                try {
                    // Llamada al backend para obtener datos de los próximos cobros previstos
                    const response = await fetch('/vencimientos/proximos_cobros', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });
            
                    const result = await response.json(); // Parsear la respuesta
                    console.log('Respuesta Próximos Cobros:', result);
            
                    // Configurar los datos del gráfico de próximos cobros previstos
                    data = {
                        labels: result.result.labels,  // Etiquetas obtenidas del backend
                        datasets: [{
                            label: 'Cobros previstos',
                            data: result.result.datasets,  // Datos obtenidos del backend
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)'
                        }]
                    };
            
                    // Opciones del gráfico de próximos cobros previstos
                    options = {
                        responsive: true,
                        scales: {
                            x: {beginAtZero: true},
                            y: {beginAtZero: true}
                        },
                        plugins: {
                            legend: {display: false}, // Ocultar leyenda
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('es-ES').format(context.parsed.y) + ' €';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error); // Manejo de errores en la carga de datos
                }
                break;

            case 'calidad_cartera':  // Propósito de mostrar la calidad de la cartera
                try {
                    // Llamada al backend para obtener los datos de calidad de la cartera
                    const response = await fetch('/riesgo/calidad_cartera', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });

                    const result = await response.json(); // Parsear la respuesta
                    console.log('Respuesta Calidad Cartera:', result);

                    // Configurar los datos del gráfico de calidad de la cartera
                    data = {
                        labels: ['Máximo', 'Alto', 'Moderado', 'Bajo', 'Mínimo'],  // Etiquetas de los niveles de riesgo
                        datasets: [{
                            label: 'Clientes',
                            data: [
                                result.result.data.maximo, 
                                result.result.data.alto, 
                                result.result.data.moderado, 
                                result.result.data.bajo, 
                                result.result.data.minimo
                            ],
                            backgroundColor: ['red', 'orange', 'yellow', 'lightgreen', 'green']  // Colores para cada nivel de riesgo
                        }]
                    };

                    // Opciones del gráfico de calidad de la cartera
                    options = {
                        responsive: true,
                        scales: {
                            x: {beginAtZero: true, title: {display: true, text: 'Riesgo de impago'}},
                            y: {beginAtZero: true},
                        },
                        plugins: {
                            legend: {
                                display: false,  // Ocultar leyenda
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error); // Manejo de errores en la carga de datos
                }
                break;
            
            case 'top_clasificaciones':
                try {
                    // Fetch data from the new backend route
                    const response = await fetch('/riesgo/top_clasificaciones', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });

                    const result = await response.json();
                    console.log('Respuesta Top Clasificaciones:', result);

                    // Prepare data for the chart
                    data = {
                        labels: result.result.result.map(d => d.cliente),  // Clientes como etiquetas
                        datasets: [{
                            label: 'Importe Concedido',
                            data: result.result.result.map(d => d.importe_concedido),  // Importes concedidos
                            backgroundColor: 'rgba(75, 192, 192, 0.5)',
                            borderColor: 'rgba(75, 192, 192, 1)'
                        }]
                    };

                    options = {
                        responsive: true,
                        scales: {
                            y: {beginAtZero: true},
                        },
                        plugins: {
                            legend: {display: false},
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('es-ES').format(context.parsed.y) + ' €';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
                break;
            
            case 'top_10_customers_impagadas':
                try {
                    // Llamada al controlador para obtener los datos desde el backend
                    const response = await fetch('/vencimientos/top_10_customers_impagadas', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });
            
                    const result = await response.json();
                    console.log('Respuesta Mayores Deudores:', result);
            
                    data = {
                        labels: result.result.labels,  // Nombres de los clientes
                        datasets: [{
                            label: 'Total Impagado',
                            data: result.result.datasets,  // Importe impagado por cliente
                            backgroundColor: 'rgba(255, 99, 132, 0.5)',
                            borderColor: 'rgba(255, 99, 132, 1)'
                        }]
                    };
            
                    options = {
                        responsive: true,
                        scales: {
                            x: {beginAtZero: true},
                            y: {beginAtZero: true}
                        },
                        plugins: {
                            legend: {display: false},
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('es-ES').format(context.parsed.y) + ' €';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    };
                } catch (error) {
                    console.error("Error Respuesta Mayores Deudores:", error);
                }
                break;

            default:
                // Configuración por defecto en caso de no coincidir el propósito
                data = { labels: [], datasets: [] };
                options = { responsive: true };
        }

        return { data, options };  // Retornar los datos y opciones para el gráfico
    }
}

// Definir el template asociado al componente
BarChartComponent.template = "credito-caucion.BarChartComponent";
