from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console

from app.config import settings
from app.orchestrator import PipelineOrchestrator
from app.schemas.export_json_schemas import export_all

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def run(brief: Path = typer.Option(..., exists=True), project: str = typer.Option(...)) -> None:
    orchestrator = PipelineOrchestrator(output_root=settings.output_root)
    orchestrator.run(brief_path=brief, project_name=project)


@app.command("export-schemas")
def export_schemas(out: Path = typer.Option(Path("app/schemas/json"))) -> None:
    export_all(out)
    console.print(f"Exported schemas to {out}")


if __name__ == "__main__":
    app()
