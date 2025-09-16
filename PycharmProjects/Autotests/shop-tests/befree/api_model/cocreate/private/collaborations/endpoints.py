class Endpoints:
    get_collaborations = "/collaborations"
    delete_collaboration = lambda self, collaboration_id: f"/collaborations/{collaboration_id}/delete"
    get_collaboration = lambda self, collaboration_id: f"/collaborations/{collaboration_id}/show"
    update_collaboration = lambda self, collaboration_id: f"/collaborations/{collaboration_id}/update"
    create_collaboration = "/collaborations/create"
    get_options = "/options"
