// plot_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    const plotContainer = document.getElementById('plotContainer');
    const addPlotBtn = document.getElementById('addPlotBtn');
    const saveDashboardBtn = document.getElementById('saveDashboardBtn');
    const shareDashboardBtn = document.getElementById('shareDashboardBtn');
    const shareModal = document.getElementById('shareModal');
    const closeShareModal = document.getElementById('closeShareModal');
    const shareLink = document.getElementById('shareLink');

    let plots = [];

    function createPlotElement(plotData) {
        const plotDiv = document.createElement('div');
        plotDiv.className = 'plot-container bg-white shadow-md rounded-lg p-4';
        const plotId = plotData.id || `plot-${Date.now()}`;
        plotDiv.id = plotId;
        plotContainer.appendChild(plotDiv);
        return { plotDiv, plotId };
    }

    function fetchDataAndCreatePlot(plotId, plotData) {
        const data = plotData.data || { labels: [], values: [] };
        const layout = plotData.layout || {
            title: 'New Plot',
            height: 400,
            width: 500
        };
        Plotly.newPlot(plotId, [{ x: data.labels, y: data.values, type: 'bar' }], layout);
        plots.push({ id: plotId, data: data, layout: layout });
    }

    function loadSavedPlots() {
        plots.forEach(plotData => {
            const { plotDiv, plotId } = createPlotElement(plotData);
            fetchDataAndCreatePlot(plotId, plotData);
        });
    }

    addPlotBtn.addEventListener('click', function() {
        const { plotDiv, plotId } = createPlotElement({});
        fetchDataAndCreatePlot(plotId, {});
    });

    saveDashboardBtn.addEventListener('click', function() {
        const dashboardData = {
            plots: plots.map(plot => ({
                id: plot.id,
                data: plot.data,
                layout: plot.layout
            }))
        };
        
        fetch('/save_dashboard', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dashboardData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Dashboard saved successfully!');
            } else {
                alert('Error saving dashboard: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error saving dashboard');
        });
    });

    shareDashboardBtn.addEventListener('click', function() {
        fetch('/save_dashboard', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                plots: plots.map(plot => ({
                    id: plot.id,
                    data: plot.data,
                    layout: plot.layout
                }))
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const shareUrl = `${window.location.origin}/shared/${encodeURIComponent(data.email)}`;
                shareLink.value = shareUrl;
                shareModal.classList.remove('hidden');
            } else {
                alert('Error generating share link: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error generating share link');
        });
    });

    closeShareModal.addEventListener('click', function() {
        shareModal.classList.add('hidden');
    });

    // Load saved plots on page load
    loadSavedPlots();
});