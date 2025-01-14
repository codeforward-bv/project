# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tests.common import Form


class TestProjectMilestone(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_project = self.env["project.project"].create({"name": "TestProject"})
        self.test_project_milestone_1 = self.env["project.milestone"].create(
            {"name": "TestMilestone_1", "project_id": self.test_project.id}
        )
        self.test_project_milestone_2 = self.env["project.milestone"].create(
            {"name": "TestMilestone_2", "project_id": self.test_project.id}
        )
        self.test_open_stage = self.env["project.task.type"].create(
            {"name": "TestOpenStage"}
        )
        self.test_close_stage = self.env["project.task.type"].create(
            {"name": "TestCloseStage", "is_closed": True}
        )
        self.test_task = self.env["project.task"].create(
            {
                "name": "TestTask",
                "project_id": self.test_project.id,
                "milestone_id": self.test_project_milestone_1.id,
                "stage_id": self.test_open_stage.id,
            }
        )
        self.env["project.task"].create(
            {
                "name": "TestTask",
                "project_id": self.test_project.id,
                "milestone_id": self.test_project_milestone_1.id,
                "stage_id": self.test_close_stage.id,
            }
        )

    def test_milestone_sequences(self):
        milestone1 = self.test_project_milestone_1
        milestone2 = self.test_project_milestone_2

        self.assertGreater(milestone2.sequence, milestone1.sequence)

    def test_milestone_progress(self):
        self.assertEqual(self.test_project_milestone_1.progress, 50)
        self.assertEqual(self.test_project_milestone_2.progress, 0)

    def test_read_group_milestone_ids(self):
        domain = [("project_id", "=", self.test_project.id)]
        Task = self.env["project.task"]
        Task = Task.with_context(default_project_id=self.test_project.id)
        grouped_tasks = Task.read_group(domain, ["name"], ["milestone_id"])
        self.assertEqual(len(grouped_tasks), 2)

    def test_sub_task(self):
        Task = self.env["project.task"]
        test_task = Task.search([("name", "=", "TestTask")], limit=1)
        self.test_project.use_milestones = False
        self.test_project.milestones_required = True
        self.test_project._onchange_use_milestones()
        with Form(Task.with_context(default_parent_id=test_task.id)) as task:
            task.name = "SubTask"
        with Form(Task) as task:
            task.project_id = self.test_project
            task.name = "SubTask"

    def test_copy_project(self):
        project = self.test_project.copy({})
        tasks = project.with_context(active_test=False).task_ids
        milestone = project.milestone_ids.filtered(
            lambda milestone: "2" not in milestone.name
        )
        self.assertEqual(tasks[0].milestone_id, milestone)
        self.assertEqual(tasks[1].milestone_id, milestone)
