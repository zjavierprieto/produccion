/** @odoo-module */

import { Component } from "@odoo/owl";
import { useRef, onMounted, onWillStart } from "@odoo/owl";

export class LineChartComponent extends Component {
    setup() {
        this.canvasRef = useRef("chart");

        // Log setup phase
        console.log('Setting up LineChartComponent');

        // Load Chart.js script dynamically if not loaded already
        onWillStart(async () => {
            console.log('onWillStart triggered');
            if (!window.Chart) {
                console.log('Chart.js not found, loading script...');
                await this.loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
                console.log('Chart.js loaded');
            } else {
                console.log('Chart.js already loaded');
            }
        });

        // Render chart on component mount
        onMounted(() => {
            console.log('Component mounted, rendering chart');
            this.renderChart();
        });
    }

    async loadJS(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                console.log('Script loaded:', src);
                resolve();
            };
            script.onerror = () => {
                console.error('Failed to load script:', src);
                reject();
            };
            document.head.appendChild(script);
        });
    }

    async renderChart() {
        if (!this.canvasRef.el) {
            console.error('Canvas element not found');
            return;
        }

        console.log('Canvas element found, rendering chart');
        const ctx = this.canvasRef.el.getContext("2d");

        // Accede al chartPurpose que se pasó desde el template
        const chartPurpose = this.props.chartPurpose;
        console.log('Chart purpose:', chartPurpose);

        const { data, options } = await this.getChartConfig(chartPurpose);
        console.log('Chart data:', data);
        console.log('Chart options:', options);

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: options,
        });

        console.log('Chart rendered');
    }

    async getChartConfig(chartPurpose) {
        let data, options;

        console.log('Getting chart config for purpose:', chartPurpose);

        switch (chartPurpose) {
            case 'incidencias_cobros':
                try {
                    // Llamada al controlador para obtener los datos desde el backend
                    const response = await fetch('/riesgo/incidencias_cobro', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}),
                    });

                    const result = await response.json();
                    console.log('Fetch Response:', result);

                    // Ahora puedes usar los datos que se han obtenido en el gráfico
                    data = {
                        labels: result.result.labels,
                        datasets: [
                            {
                                label: 'Avisos falta de pago',
                                data: result.result.datasets.avisos_falta_pago,
                                borderColor: 'orange',
                                backgroundColor: 'rgba(255, 221, 0, 0.5)',
                                fill: true,
                                pointRadius: 3,
                                pointHoverRadius: 5,
                                borderWidth: 2,
                                hoverBorderWidth: 8,
                            },
                            {
                                label: 'Prórrogas',
                                data: result.result.datasets.prorrogas,
                                borderColor: 'darkorange',
                                backgroundColor: 'rgba(255, 140, 0, 0.5)',
                                fill: true,
                                pointRadius: 3,
                                pointHoverRadius: 5,
                                borderWidth: 2,
                                hoverBorderWidth: 8,
                            },
                            {
                                label: 'Siniestros',
                                data: result.result.datasets.siniestros,
                                borderColor: 'red',
                                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                                fill: true,
                                pointRadius: 3,
                                pointHoverRadius: 5,
                                borderWidth: 2,
                                hoverBorderWidth: 8,
                            }
                        ]
                    };

                    options = {
                        responsive: true,
                        plugins: {
                            legend: { display: true, position: 'top' },
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
                        },
                        scales: {
                            y: { beginAtZero: true },
                            x: {},
                        },
                    };
                    
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
                break;


            default:
                data = { labels: [], datasets: [] };
                options = { responsive: true };
        }

        console.log('Data:', data);
        console.log('Options:', options);

        return { data, options };
    }
}

LineChartComponent.template = "credito-caucion.LineChartComponent";
