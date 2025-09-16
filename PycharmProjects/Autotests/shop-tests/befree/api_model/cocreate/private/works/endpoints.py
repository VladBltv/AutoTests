class Endpoints:
    get_works = "/works"
    delete_work = lambda self, work_id: f"/works/{work_id}/delete"
    get_work = lambda self, work_id: f"/works/{work_id}/show"
    update_work = lambda self, work_id: f"/works/{work_id}/update"
