function distinct(value, index, self) {
    return self.indexOf(value) === index;
}

function buildChart(electionSequences, labels, id) {
    let ctx = document.getElementById(id).getContext('2d');
    // let colors = chroma.scale(['#00a6a8', '#457bd5', '#3659da', '#e82168', '#c61e7e', '#8e28b1']).colors(labels.length);
    // let colors = chroma.scale(['#00a6a8', '#e82168']).mode('lch').colors(labels.length);
    // let colors = chroma.scale(['#99d594', '#2747db', '#ef40ae', '#EA5252', '#fc8d59']).colors(labels.length);
    // let colors = chroma.scale(['#d53e4f','#fc8d59','#FFDA70','#CDE160','#89D583','#3288bd']).mode('rgb').colors(labels.length);
    let colors = chroma.scale(['#7B55A7', '#d53e4f','#fc8d59','#FFDA70','#89D583','#3288bd']).mode('rgb').colors(labels.length);
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