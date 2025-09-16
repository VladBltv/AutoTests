class Endpoints:
    get_projects = "/projects"
    get_contest = lambda self, contest_id: f"/contests/{contest_id}/show"
