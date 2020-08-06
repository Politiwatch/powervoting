function distinct(value, index, self) {
    return self.indexOf(value) === index;
}

function buildChart(electionSequences, labels, id) {
    let ctx = document.getElementById(id).getContext('2d');
    // let colors = chroma.scale('Spectral').colors(labels.length);
    let colors = chroma.scale(['#5DDBCC', '#DB5D67']).mode('lch').colors(labels.length);
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: electionSequences.map(s => s.map(e => e.year)).flat().filter(distinct).sort((a, b) => a - b),
            datasets: electionSequences.map((s, i) => {
                return {
                    label: labels[i],
                    data: s.sort((a, b) => a.year - b.year).map(e => {
                        return {
                            x: e.year,
                            y: (e.scores.closeness * 100).toFixed(2),
                            label: `${labels[i]}: ${(e.scores.closeness * 100).toFixed(2)}% Closeness (${e.totalvotes.toLocaleString()} votes)`,
                        }
                    }),
                    borderColor: colors[i],
                    backgroundColor: colors[i],
                    fill: false,
                }
            }),
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    label: function (tooltipItem, data) {
                        return data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].label;
                    },
                }
            },
        }
    });
}