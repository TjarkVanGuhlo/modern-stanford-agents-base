"""
Author: Joon Sung Park (joonspk@stanford.edu)
File: views.py
"""

import datetime
import json
import os

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from global_methods import check_if_file_exists, find_filenames

from .validation import (
    TEMP_STORAGE_ROOT,
    ValidationError,
    safe_storage_path,
    validate_camera_data,
    validate_environment_request,
    validate_update_request,
)


def landing(request):
    context = {}
    template = "landing/landing.html"
    return render(request, template, context)


def demo(request, sim_code, step, play_speed="2"):
    move_file = f"compressed_storage/{sim_code}/master_movement.json"
    meta_file = f"compressed_storage/{sim_code}/meta.json"
    step = int(step)
    play_speed_opt = {"1": 1, "2": 2, "3": 4, "4": 8, "5": 16, "6": 32}
    if play_speed not in play_speed_opt:
        play_speed = 2
    else:
        play_speed = play_speed_opt[play_speed]

    # Loading the basic meta information about the simulation.
    meta = {}
    with open(meta_file) as json_file:
        meta = json.load(json_file)

    sec_per_step = meta["sec_per_step"]
    start_datetime = datetime.datetime.strptime(
        meta["start_date"] + " 00:00:00", "%B %d, %Y %H:%M:%S"
    )
    for i in range(step):
        start_datetime += datetime.timedelta(seconds=sec_per_step)
    start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Loading the movement file
    raw_all_movement = {}
    with open(move_file) as json_file:
        raw_all_movement = json.load(json_file)

    # Loading all names of the personas
    persona_names = []
    persona_names_set = set()
    for p in list(raw_all_movement["0"].keys()):
        persona_names += [
            {
                "original": p,
                "underscore": p.replace(" ", "_"),
                "initial": p[0] + p.split(" ")[-1][0],
            }
        ]
        persona_names_set.add(p)

    # <all_movement> is the main movement variable that we are passing to the
    # frontend. Whereas we use ajax scheme to communicate steps to the frontend
    # during the simulation stage, for this demo, we send all movement
    # information in one step.
    all_movement = {}

    # Preparing the initial step.
    # <init_prep> sets the locations and descriptions of all agents at the
    # beginning of the demo determined by <step>.
    init_prep = {}
    for int_key in range(step + 1):
        key = str(int_key)
        val = raw_all_movement[key]
        for p in persona_names_set:
            if p in val:
                init_prep[p] = val[p]
    persona_init_pos = {}
    for p in persona_names_set:
        persona_init_pos[p.replace(" ", "_")] = init_prep[p]["movement"]
    all_movement[step] = init_prep

    # Finish loading <all_movement>
    for int_key in range(step + 1, len(raw_all_movement.keys())):
        all_movement[int_key] = raw_all_movement[str(int_key)]

    context = {
        "sim_code": sim_code,
        "step": step,
        "persona_names": persona_names,
        "persona_init_pos": json.dumps(persona_init_pos),
        "all_movement": json.dumps(all_movement),
        "start_datetime": start_datetime,
        "sec_per_step": sec_per_step,
        "play_speed": play_speed,
        "mode": "demo",
    }
    template = "demo/demo.html"

    return render(request, template, context)


def home(request):
    f_curr_sim_code = "temp_storage/curr_sim_code.json"
    f_curr_step = "temp_storage/curr_step.json"

    if not check_if_file_exists(f_curr_step):
        context = {}
        template = "home/error_start_backend.html"
        return render(request, template, context)

    with open(f_curr_sim_code) as json_file:
        sim_code = json.load(json_file)["sim_code"]

    with open(f_curr_step) as json_file:
        step = json.load(json_file)["step"]

    os.remove(f_curr_step)

    persona_names = []
    persona_names_set = set()
    for i in find_filenames(f"storage/{sim_code}/personas", ""):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)

    persona_init_pos = []
    file_count = []
    for i in find_filenames(f"storage/{sim_code}/environment", ".json"):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            file_count += [int(x.split(".")[0])]
    curr_json = f"storage/{sim_code}/environment/{str(max(file_count))}.json"
    with open(curr_json) as json_file:
        persona_init_pos_dict = json.load(json_file)
        for key, val in persona_init_pos_dict.items():
            if key in persona_names_set:
                persona_init_pos += [[key, val["x"], val["y"]]]

    context = {
        "sim_code": sim_code,
        "step": step,
        "persona_names": persona_names,
        "persona_init_pos": persona_init_pos,
        "mode": "simulate",
    }
    template = "home/home.html"
    return render(request, template, context)


def replay(request, sim_code, step):
    sim_code = sim_code
    step = int(step)

    persona_names = []
    persona_names_set = set()
    for i in find_filenames(f"storage/{sim_code}/personas", ""):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)

    persona_init_pos = []
    file_count = []
    for i in find_filenames(f"storage/{sim_code}/environment", ".json"):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            file_count += [int(x.split(".")[0])]
    curr_json = f"storage/{sim_code}/environment/{str(max(file_count))}.json"
    with open(curr_json) as json_file:
        persona_init_pos_dict = json.load(json_file)
        for key, val in persona_init_pos_dict.items():
            if key in persona_names_set:
                persona_init_pos += [[key, val["x"], val["y"]]]

    context = {
        "sim_code": sim_code,
        "step": step,
        "persona_names": persona_names,
        "persona_init_pos": persona_init_pos,
        "mode": "replay",
    }
    template = "home/home.html"
    return render(request, template, context)


def replay_persona_state(request, sim_code, step, persona_name):
    sim_code = sim_code
    step = int(step)

    persona_name_underscore = persona_name
    persona_name = " ".join(persona_name.split("_"))
    memory = os.path.join(
        "storage", sim_code, "personas", persona_name, "bootstrap_memory"
    )
    if not os.path.exists(memory):
        memory = os.path.join(
            "compressed_storage", sim_code, "personas", persona_name, "bootstrap_memory"
        )

    with open(os.path.join(memory, "scratch.json")) as json_file:
        scratch = json.load(json_file)

    with open(os.path.join(memory, "spatial_memory.json")) as json_file:
        spatial = json.load(json_file)

    with open(os.path.join(memory, "associative_memory", "nodes.json")) as json_file:
        associative = json.load(json_file)

    a_mem_event = []
    a_mem_chat = []
    a_mem_thought = []

    for count in range(len(associative.keys()), 0, -1):
        node_id = f"node_{str(count)}"
        node_details = associative[node_id]

        if node_details["type"] == "event":
            a_mem_event += [node_details]

        elif node_details["type"] == "chat":
            a_mem_chat += [node_details]

        elif node_details["type"] == "thought":
            a_mem_thought += [node_details]

    context = {
        "sim_code": sim_code,
        "step": step,
        "persona_name": persona_name,
        "persona_name_underscore": persona_name_underscore,
        "scratch": scratch,
        "spatial": spatial,
        "a_mem_event": a_mem_event,
        "a_mem_chat": a_mem_chat,
        "a_mem_thought": a_mem_thought,
    }
    template = "persona_state/persona_state.html"
    return render(request, template, context)


def path_tester(request):
    context = {}
    template = "path_tester/path_tester.html"
    return render(request, template, context)


@csrf_exempt
@require_POST
def process_environment(request: HttpRequest) -> HttpResponse:
    """Receive frontend visual world information and write to storage.

    This endpoint receives environment state from the frontend and persists it
    to the storage directory for the backend simulation server to read.

    Args:
        request: Django request containing JSON with step, sim_code, environment.

    Returns:
        HttpResponse with "received" on success, or HTTP 400 on validation failure.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON in request body", status=400)

    try:
        step, sim_code, environment = validate_environment_request(data)
    except ValidationError as e:
        field_info = f" ({e.field})" if e.field else ""
        return HttpResponse(f"Validation error{field_info}: {e.message}", status=400)

    # Build safe path preventing traversal attacks
    output_path = safe_storage_path(sim_code, "environment", f"{step}.json")
    if output_path is None:
        return HttpResponse("Invalid path parameters", status=400)

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as outfile:
        json.dump(environment, outfile, indent=2)

    return HttpResponse("received")


@csrf_exempt
@require_POST
def update_environment(request: HttpRequest) -> HttpResponse:
    """Send backend persona movement data to the frontend.

    This endpoint reads movement data computed by the backend simulation
    and returns it to the frontend for visualization.

    Args:
        request: Django request containing JSON with step and sim_code.

    Returns:
        JsonResponse with movement data, or HTTP 400 on validation failure.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON in request body", status=400)

    try:
        step, sim_code = validate_update_request(data)
    except ValidationError as e:
        field_info = f" ({e.field})" if e.field else ""
        return HttpResponse(f"Validation error{field_info}: {e.message}", status=400)

    # Build safe path preventing traversal attacks
    movement_path = safe_storage_path(sim_code, "movement", f"{step}.json")
    if movement_path is None:
        return HttpResponse("Invalid path parameters", status=400)

    response_data: dict = {"<step>": -1}
    if movement_path.exists():
        with open(movement_path) as json_file:
            response_data = json.load(json_file)
            response_data["<step>"] = step

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def path_tester_update(request: HttpRequest) -> HttpResponse:
    """Save camera position for path tester utility.

    This endpoint receives camera/viewport data from the path tester frontend
    and persists it to temp storage for the backend path testing utility.

    Args:
        request: Django request containing JSON with camera data.

    Returns:
        HttpResponse with "received" on success, or HTTP 400 on validation failure.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON in request body", status=400)

    try:
        camera = validate_camera_data(data)
    except ValidationError as e:
        field_info = f" ({e.field})" if e.field else ""
        return HttpResponse(f"Validation error{field_info}: {e.message}", status=400)

    # Use fixed path in temp_storage (no user-controlled components)
    output_path = TEMP_STORAGE_ROOT / "path_tester_env.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as outfile:
        json.dump(camera, outfile, indent=2)

    return HttpResponse("received")
