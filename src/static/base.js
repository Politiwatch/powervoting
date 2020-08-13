function distinct(value, index, self) {
    return self.indexOf(value) === index;
}

function buildChart(electionSequences, labels, id) {
    let ctx = document.getElementById(id).getContext('2d');
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
                            x: parseInt(e.year),
                            y: (e.scores.closeness * 100).toFixed(2),
                            title: `${e.year}: ${labels[i]}`,
                            label: `${(e.scores.closeness * 100).toFixed(2)}% Closeness (${e.totalvotes.toLocaleString()} votes)`,
                        }
                    }),
                    borderColor: colors[i],
                    backgroundColor: colors[i],
                    fill: false,
                }
            }),
        },
        options: {
            maintainAspectRatio: false,
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
                    title: function (tooltipItems, data) {
                        return data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index].title;
                    }
                }
            },
        }
    });
}

function highlightComparisons() {
    let comparisons = [...document.querySelectorAll(".comparison")];
    let groups = comparisons.map(e => e.getAttribute("data-comparison-group")).filter(distinct);
    for (let group of groups) {
        let highest = -1;
        let highestElems = [];
        let elems = document.querySelectorAll(`.comparison[data-comparison-group="${group}"]`);
        if (elems.length > 1) {
            for (let elem of elems) {
                let val = parseFloat(elem.textContent);
                if (val > highest) {
                    highest = val;
                    highestElems = [elem];
                } else if (val == highest) {
                    highestElems.push(elem);
                }
            }
            if (highestElems.length > 1) {
                highestElems.forEach(x => x.classList.add("comparison-tie"));
            } else {
                highestElems.forEach(x => x.classList.add("comparison-highest-in-group"));
            }
        }
    }
}

function loadTippy() {
    tippy("[data-tippy-content]");
}

window.addEventListener("load", highlightComparisons);
window.addEventListener("load", loadTippy);