"use client";

import Link from "next/link";
import { Project } from "@/lib/api";

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const statusLabels: Record<string, string> = {
    created: "Created",
    concepts_generated: "Concepts",
    concept_selected: "Concept Selected",
    script_generated: "Script",
    complete: "Complete",
  };

  return (
    <Link href={`/projects/${project.id}`}>
      <div className="card hover:shadow-md transition-shadow cursor-pointer">
        <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-sm text-gray-500">
            Status:
          </span>
          <span className="text-sm font-medium text-blue-600">
            {statusLabels[project.status] || project.status}
          </span>
        </div>
        <div className="mt-1 text-xs text-gray-400">
          Created {new Date(project.created_at).toLocaleDateString()}
        </div>
      </div>
    </Link>
  );
}
