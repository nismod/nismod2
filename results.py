import matplotlib
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
import os

from smif.controller.build import get_model_run_definition, build_model_run
from smif.controller.load import load_resolution_sets
from smif.data_layer.datafile_interface import DatafileInterface
from smif.data_layer.data_handle import DataHandle
from smif.model.scenario_model import ScenarioModel

handler = DatafileInterface('./')

available_modelrun = widgets.RadioButtons(
    description='Model Runs:',
    options=sorted([x['name'] for x in handler.read_sos_model_runs()]))

plt.ioff()
dep_ax=plt.gca()

show_dep_graph = widgets.Output()

global models
global store
global modelrun
global dep_graph

def plot_dep_graph(dep_graph):
    show_dep_graph.clear_output(wait=True)
    with show_dep_graph:
        dep_ax.clear()
        dep_graph_relabelled = nx.relabel_nodes(dep_graph, {x: x.name for x in dep_graph}, copy=True)
        nx.draw(dep_graph_relabelled, ax=dep_ax, with_labels=True)
        display(dep_ax.figure)

def load_model_run_results(click):
    model_run_config = get_model_run_definition('./', available_modelrun.value)

    global modelrun
    modelrun = build_model_run(model_run_config)

    global store
    store = DatafileInterface('./')

    global dep_graph
    modelrun.sos_model.make_dependency_graph()
    dep_graph = modelrun.sos_model.dependency_graph
    try:
        plot_dep_graph(dep_graph)
    except ValueError:
        pass
    
    global models
    models = modelrun.sos_model.models 

    initialise_viewer(dep_graph, modelrun, models)
    initialise_model_viewer(dep_graph, models)

def initialise_viewer(dep_graph, modelrun, models):

    year.options = modelrun.model_horizon
    model.options = [x.name for x in dep_graph.nodes()]
    from_model.options = [x.name for x in dep_graph.predecessors(models[model.value])]
    to_model.options = [x.name for x in dep_graph[models[model.value]]]
    data_in.options = get_predecessor_outputs(models, model.value, from_model.value)
    data_out.options = get_predecessor_outputs(models, to_model.value, model.value)

    click_from(None)
    click_to(None)


load_button = widgets.Button(
    description="Load Results")

load_button.on_click(load_model_run_results)

def get_predecessor_outputs(models, model_name, source_model_name):
    """
    
    Returns
    =======
    list
    """
    outputs = []
    if model_name in models and source_model_name in models:
        deps = models[model_name].deps
        for x in deps.values():
            if x.source_model.name == source_model_name:
                outputs.append(x.source.name)
    return sorted(outputs)

def get_outputs(models, model_name):
    """
    
    Returns
    =======
    list
    """
    outputs = []
    if model_name in models:
        outputs = sorted(models[model_name].outputs.names)
    return outputs

def plot_subgraph(model):
    d = [x for x in dep_graph.predecessors(model)]
    d.append(model)
    sub_graph = dep_graph.subgraph(d)
    sub_graph_relabelled = nx.relabel_nodes(sub_graph, {x: x.name for x in sub_graph}, copy=True)
    nx.draw(sub_graph_relabelled, with_labels=True)

def plot_results(store, modelrun, model, parameter, year, axes):
    axes.clear()
    
    handle = DataHandle(store, modelrun.name, year, modelrun.model_horizon, model,
    decision_iteration=0)
    
    spatial_resolution = model.outputs[parameter].spatial_resolution
    temporal_resolution = model.outputs[parameter].temporal_resolution
    
    if isinstance(model, ScenarioModel):
        data = handle._store.read_scenario_data(
                                                model.scenario_name,  # read from scenario
                                                parameter,  # using output (parameter) name
                                                spatial_resolution.name,
                                                temporal_resolution.name,
                                                year)
        data = data.sum(axis=0)
#         names = temporal_resolution.get_entry_names()
#         plt.plot(names, data)
        plt.plot(data)
    else:
        data = handle.get_results(parameter)
        data = data.sum(axis=0)
        plt.plot(data)
    
    units = model.outputs.get_units(parameter)
    axes.set_ylabel(units)
    axes.set_xlabel(temporal_resolution.name)
    axes.set_title(model.name + ': ' + parameter)
    axes.set_ylim(0,)
    
    display(axes.figure)

def on_model_change(change):
    if model.value in models:
        from_model.options = [x.name for x in dep_graph.predecessors(models[model.value])]
        to_model.options = [x.name for x in dep_graph[models[model.value]]]

def from_model_change(change):
    if from_model.value in models:
        data_in.options = get_predecessor_outputs(models, model.value, from_model.value)
    else:
        data_in.options = []

def to_model_change(change):
    if to_model.value in models:
        data_out.options = get_predecessor_outputs(models, to_model.value, model.value)     
    else:
        data_out.options = []

def click_from(b):
    outputs_from.clear_output(wait=True)
    if from_model.value in models and model.value and data_in.value:
        with outputs_from:
            plot_results(store, modelrun, models[from_model.value], data_in.value, year.value, ax_from)

def click_to(b):
    outputs_to.clear_output(wait=True)
    if model.value in models and to_model.value and data_out.value:
        with outputs_to:
            plot_results(store, modelrun, models[model.value], data_out.value, year.value, ax_to)

year = widgets.Dropdown(
    options=[],
    description='Year:',
    disabled=False)

model = widgets.Dropdown(
    options=[],
    description='Model:',
    disabled=False
)
model.observe(on_model_change, names='value')

from_model = widgets.Dropdown(
    options=[],
    description='From Model:',
    disabled=False)
from_model.observe(from_model_change, names='value')

to_model = widgets.Dropdown(
    options=[],
    description='To Model:',
    disabled=False)
to_model.observe(to_model_change, names='value')

data_in = widgets.Dropdown(
    options=[],
    description='Data In:',
    disabled=False)

data_out = widgets.Dropdown(
    options=[],
    description='Data Out:',
    disabled=False)

outputs_from = widgets.Output()
ax_from=plt.gca()
outputs_to = widgets.Output()
ax_to=plt.gca()

button_from = widgets.Button(
    description='Show')
button_to = widgets.Button(
    description='Show')

button_from.on_click(click_from)
button_to.on_click(click_to)




# In[ ]:

def initialise_model_viewer(dep_graph, models):
    model_only.options = [x.name for x in dep_graph.nodes()]
    outputs.options = get_outputs(models, model_only.value)
    outputs_change(None)


output_ax = plt.gca()

model_only = widgets.Dropdown(
    options=[],
    description='Model:',
    disabled=False,
)

outputs = widgets.Dropdown(
    options=[],
    description='Data Out:',
    disabled=False,
)

plot = widgets.Output()


def model_only_change(change):
    if model_only.value in models:
        outputs.options = get_outputs(models, model_only.value)
        
def outputs_change(change):
    plot.clear_output(wait=True)
    if outputs.value:
        with plot:
            plot_results(store, modelrun, models[model_only.value], outputs.value, year.value, output_ax)

model_only.observe(model_only_change, names='value')
outputs.observe(outputs_change, names='value')



choose_modelrun = widgets.VBox([
    widgets.HBox([available_modelrun, load_button]), 
    show_dep_graph
])

view_results = widgets.VBox([
    widgets.HBox([
        year, model]),
        widgets.HBox([
            widgets.VBox([from_model, data_in, button_from, outputs_from]), 
            widgets.VBox([to_model, data_out, button_to, outputs_to
                    ])
        ])
                 ])

view_outputs = widgets.VBox([model_only, outputs, plot])