function fetchData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    fetch(`https://619d-200-137-83-157.ngrok-free.app/data?start=${encodeURIComponent(startDate)}&end=${encodeURIComponent(endDate)}`, {
        method: 'GET',
        headers: {
            'ngrok-skip-browser-warning': 'skip-browser-warning'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            plotData(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function plotData(data) {
    const variables = ['temperature', 'humidity', 'wind_speed', 'pressure', 'rainfall', 'altitude', 'lux', 'battery_voltage'];
    const timestamps = data.map(d => new Date(d.timestamp)); // Todos os gráficos compartilham o eixo X (tempo)

    const chartsContainer = document.getElementById('chartsContainer');
    chartsContainer.innerHTML = ''; // Limpar os gráficos anteriores

    variables.forEach(variable => {
        // Criar uma div e canvas para cada gráfico
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container';

        const canvas = document.createElement('canvas');
        chartDiv.appendChild(canvas);
        chartsContainer.appendChild(chartDiv);

        const ctx = canvas.getContext('2d');
        const values = data.map(d => d[variable]);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: variable.charAt(0).toUpperCase() + variable.slice(1),
                    data: values,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute'
                        }
                    }
                }
            }
        });
    });
}
