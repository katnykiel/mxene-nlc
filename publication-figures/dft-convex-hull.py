# query the relaxed DFT structures and energies from the atomate2 mongodb
from fireworks import LaunchPad
from kat.atomate2.utils import get_convex_hulls
from kat.plotting import get_plot_layout
from jobflow import SETTINGS

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()
lpad = LaunchPad.auto_load()

# Query for the relaxation simulations
docs = list(store.query(
    {
        "metadata.tags": {
            "$all": [
                "elastic-dft-workflow",
            ]
        },
        "name": "tight relax 2",
        "output.chemsys": "C-Ta",
    }
))

figs, diagrams = get_convex_hulls(docs, write_results=False, search_db = False, return_diagrams=True)

fig = figs[0]

fig.update_layout(get_plot_layout())

fig.update_layout(
    yaxis_title="E<sub>hull</sub> (eV/atom)",
    width=600,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(xanchor="right", yanchor="bottom", x=1, y=0, orientation="v"),
    xaxis=dict(
        automargin=True, 
        showgrid=False, 
        ticks="inside", 
        mirror="allticks", 
        ticklen=6, 
        tickwidth=1,
        range=[0.2,0.6], 
        tickcolor='black', 
        minor=dict(ticks="inside", ticklen=3, tickwidth=1, tickcolor='grey')
    ),
    yaxis=dict(
        automargin=True, 
        showgrid=False, 
        ticks="inside", 
        mirror="allticks", 
        ticklen=6, 
        tickwidth=1, 
        tickcolor='black', 
        range=[-0.69,-0.31],
        minor=dict(ticks="inside", ticklen=3, tickwidth=1, tickcolor='grey')
    ),
    font=dict(size=14)
)

fig.data[1].update(showlegend=False)

    
fig.data[2].name = "MP: Stable"
fig.data[3].name = "MP: Unstable"
fig.data[4].name = "This Work"

fig.data[2].marker.color = 'rgb(66,66,66)'
fig.data[4].marker.color = 'rgb(99,188,179)'

fig.data = fig.data[0:1] + fig.data[-1:] + fig.data[1:-1]

fig.update_layout(
    font=dict(family="Nirmala UI"),
)

fig.show()

fig.write_image("dft-convex-hull.png",scale=3)