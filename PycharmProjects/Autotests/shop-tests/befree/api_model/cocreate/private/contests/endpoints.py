class Endpoints:
    get_contests = "/contests"
    delete_contest = lambda self, contest_id: f"/contests/{contest_id}/delete"
    get_contest = lambda self, contest_id: f"/contests/{contest_id}/show"
    update_contest = lambda self, contest_id: f"/contests/{contest_id}/update"
    create_contest = "/contests/create"
