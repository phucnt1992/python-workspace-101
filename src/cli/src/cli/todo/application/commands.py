from domain.todo import Todo

from cli.todo.storage import TodoRepository, TodoSessionRunner
from cli.todo.presentation import TodoPresenter


class TodoCommands:
    def __init__(
        self,
        runner: TodoSessionRunner,
        repository: TodoRepository,
        presenter: TodoPresenter,
    ) -> None:
        self._runner = runner
        self._repository = repository
        self._presenter = presenter

    def list_todos(self) -> None:
        todos = self._runner.run(self._repository.list_all)
        if not todos:
            self._presenter.show_empty_list()
            return
        self._presenter.show_todos(todos)

    def create(self, title: str, description: str | None) -> None:
        todo = self._runner.run(lambda session: self._repository.create(session, title, description))
        self._presenter.show_created(todo)

    def update(
        self,
        todo_id: int,
        title: str | None,
        description: str | None,
    ) -> None:
        todo = self._runner.run(
            lambda session: self._repository.update(session, todo_id, title=title, description=description)
        )
        self._presenter.show_updated(self._require_todo(todo, todo_id))

    def delete(self, todo_id: int) -> None:
        deleted = self._runner.run(lambda session: self._repository.delete(session, todo_id))
        if not deleted:
            self._presenter.exit_not_found(todo_id)
        self._presenter.show_deleted(todo_id)

    def complete(self, todo_id: int) -> None:
        self._set_completed(todo_id, completed=True)

    def reopen(self, todo_id: int) -> None:
        self._set_completed(todo_id, completed=False)

    def _set_completed(self, todo_id: int, *, completed: bool) -> None:
        todo = self._runner.run(
            lambda session: self._repository.set_completed(session, todo_id, completed)
        )
        self._presenter.show_todo(self._require_todo(todo, todo_id))

    def _require_todo(self, todo: Todo | None, todo_id: int) -> Todo:
        if todo is None:
            self._presenter.exit_not_found(todo_id)
        return todo
