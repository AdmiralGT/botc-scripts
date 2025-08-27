scripts(request, pk: int, version: str) -> JsonResponse:
    """Get similar scripts via AJAX."""
    if request.method != "GET":
        raise Http404("Method not allowed")
        
    current_script = get_object_or_404(
        models.ScriptVersion,
        script__pk=pk,
        version=version
    )
    
    # Get similar scripts for each type
    similarity_data = {
        models.ScriptTypes.TEENSYVILLE.value: {},
        models.ScriptTypes.FULL.value: {}
    }
    
    # Query only latest clocktower scripts
    candidates = models.ScriptVersion.objects.filter(
        latest=True,
        homebrewiness=models.Homebrewiness.CLOCKTOWER
    ).exclude(pk=current_script.pk).order_by("pk")
    
    for script_version in candidates:
        similarity_score = ScriptService.calculate_similarity(
            current_script.content,
            script_version.content,
            current_script.script_type == script_version.script_type
        )
        similarity_data[script_version.script_type][script_version] = similarity_score
    
    # Format results
    def format_similarity_result(item):
        script_version, score = item
        return {
            "value": score,
            "name": script_version.script.name,
            "scriptPK": script_version.script.pk,
        }
    
    teensyville_results = list(map(
        format_similarity_result,
        sorted(
            similarity_data[models.ScriptTypes.TEENSYVILLE].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ))
    
    full_results = list(map(
        format_similarity_result,
        sorted(
            similarity_data[models.ScriptTypes.FULL].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ))
    
    return JsonResponse({
        "teensyville": teensyville_results,
        "full": full_results
    })


def _get_edition_from_request(request) -> models.Edition:
    """Helper to get edition from request."""
    if "selected_edition" in request.GET:
        edition_label = request.GET.get("selected_edition")
        for edition in models.Edition:
            if edition.label == edition_label:
                return edition
    return models.Edition.ALL


def _json_file_response(name: str, content: List[Dict]) -> FileResponse:
    """Helper to create JSON file response."""
    json_str = js.JSONEncoder(ensure_ascii=False).encode(content)
    temp_file = TemporaryFile()
    temp_file.write(json_str.encode("utf-8"))
    temp_file.flush()
    temp_file.seek(0)
    return FileResponse(temp_file, as_attachment=True, filename=f"{name}.json")
