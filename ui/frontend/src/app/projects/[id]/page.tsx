"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  projectsApi,
  pipelineApi,
  ProjectDetail,
  ConceptBatch,
  ScriptArtifact,
  VideoPromptArtifact,
  FinalPackage,
} from "@/lib/api";
import { PipelineStepper } from "@/components/PipelineStepper";
import { ConceptList } from "@/components/ConceptList";
import { ScriptViewer } from "@/components/ScriptViewer";
import { VideoPromptViewer } from "@/components/VideoPromptViewer";

const PIPELINE_STEPS = [
  { id: 1, label: "Setup", status: "complete" as const },
  { id: 2, label: "Concepts", status: "pending" as const },
  { id: 3, label: "Script", status: "pending" as const },
  { id: 4, label: "Video Prompts", status: "pending" as const },
  { id: 5, label: "Export", status: "pending" as const },
];

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [concepts, setConcepts] = useState<ConceptBatch | null>(null);
  const [script, setScript] = useState<ScriptArtifact | null>(null);
  const [videoPrompts, setVideoPrompts] = useState<VideoPromptArtifact | null>(null);
  const [finalPackage, setFinalPackage] = useState<FinalPackage | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(projectId);
      setProject(data);

      // Load existing data
      const conceptsData = await pipelineApi.getConcepts(projectId);
      if (conceptsData.exists && conceptsData.concepts) {
        setConcepts(conceptsData.concepts);
      }

      const scriptData = await pipelineApi.getScript(projectId);
      if (scriptData.exists && scriptData.script) {
        setScript(scriptData.script);
      }

      const videoPromptsData = await pipelineApi.getVideoPrompts(projectId);
      if (videoPromptsData.exists && videoPromptsData.video_prompts) {
        setVideoPrompts(videoPromptsData.video_prompts);
      }

      const finalPackageData = await pipelineApi.getFinalPackage(projectId);
      if (finalPackageData.exists && finalPackageData.final_package) {
        setFinalPackage(finalPackageData.final_package);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    }
  };

  const handleGenerateConcepts = async () => {
    try {
      setLoading("concepts");
      setError(null);
      const data = await pipelineApi.generateConcepts(projectId);
      if (data.success && data.concepts) {
        setConcepts(data.concepts);
        await loadProject();
      } else {
        setError(data.error || "Failed to generate concepts");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate concepts");
    } finally {
      setLoading(null);
    }
  };

  const handleSelectConcept = async (conceptId: string) => {
    try {
      setLoading("selection");
      setError(null);
      const data = await pipelineApi.selectConcept(projectId, conceptId);
      if (data.success) {
        await loadProject();
      } else {
        setError(data.error || "Failed to select concept");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to select concept");
    } finally {
      setLoading(null);
    }
  };

  const handleGenerateScript = async () => {
    try {
      setLoading("script");
      setError(null);
      const data = await pipelineApi.generateScript(projectId);
      if (data.success && data.script) {
        setScript(data.script);
        await loadProject();
      } else {
        setError(data.error || "Failed to generate script");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate script");
    } finally {
      setLoading(null);
    }
  };

  const handleGenerateVideoPrompts = async () => {
    try {
      setLoading("video-prompts");
      setError(null);
      const data = await pipelineApi.generateVideoPrompts(projectId);
      if (data.success && data.video_prompts) {
        setVideoPrompts(data.video_prompts);
        await loadProject();
      } else {
        setError(data.error || "Failed to generate video prompts");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate video prompts");
    } finally {
      setLoading(null);
    }
  };

  const handleDownloadFinalPackage = () => {
    if (finalPackage) {
      const dataStr = JSON.stringify(finalPackage, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `final-package-${projectId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  const getCurrentStep = () => {
    if (!project) return 1;
    if (project.status === "complete") return 5;
    return project.current_step + 1;
  };

  if (!project) {
    return (
      <div className="text-center py-12 text-gray-500">
        {error ? (
          <div className="space-y-4">
            <div className="text-red-600">{error}</div>
            <Link href="/" className="btn btn-secondary">
              Back to Projects
            </Link>
          </div>
        ) : (
          "Loading..."
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline">
          ← Back to Projects
        </Link>
      </div>

      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
        <div className="mt-2 text-sm text-gray-600">
          Status: <span className="font-medium capitalize">{project.status.replace(/_/g, " ")}</span>
        </div>
      </div>

      <div className="card">
        <PipelineStepper currentStep={getCurrentStep()} steps={PIPELINE_STEPS} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Concepts Section */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Step 1: Generate Concepts</h2>

        {!concepts ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Generate 5 video concepts based on your channel brief.</p>
            <button
              className="btn btn-primary"
              onClick={handleGenerateConcepts}
              disabled={loading === "concepts"}
            >
              {loading === "concepts" ? "Generating..." : "Generate Concepts"}
            </button>
          </div>
        ) : project.status === "concepts_generated" || project.status === "concept_selected" || project.current_step >= 1 ? (
          <div className="space-y-4">
            <p className="text-green-600">✓ Concepts generated</p>
            {project.status === "concepts_generated" && (
              <ConceptList
                concepts={concepts.concepts}
                onSelect={handleSelectConcept}
                loading={loading === "selection"}
              />
            )}
            {project.status !== "concepts_generated" && (
              <p className="text-blue-600">Concept selected. Moving to script generation...</p>
            )}
          </div>
        ) : (
          <div className="text-green-600">✓ Concepts generated and selected</div>
        )}
      </div>

      {/* Script Section */}
      {(project.status === "concept_selected" || project.current_step >= 2) && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Step 2: Generate Script</h2>

          {!script ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">Generate a structured script for your selected concept.</p>
              <button
                className="btn btn-primary"
                onClick={handleGenerateScript}
                disabled={loading === "script"}
              >
                {loading === "script" ? "Generating..." : "Generate Script"}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-green-600">✓ Script generated</p>
              <ScriptViewer script={script} />
            </div>
          )}
        </div>
      )}

      {/* Video Prompts Section */}
      {(project.status === "script_generated" || project.current_step >= 3) && script && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Step 3: Generate Video Prompts</h2>

          {!videoPrompts ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                Generate AI-ready video prompts from your script.
              </p>
              <button
                className="btn btn-primary"
                onClick={handleGenerateVideoPrompts}
                disabled={loading === "video-prompts"}
              >
                {loading === "video-prompts" ? "Generating..." : "Generate Video Prompts"}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-green-600">✓ Video prompts generated</p>
              <VideoPromptViewer videoPrompts={videoPrompts} />
            </div>
          )}
        </div>
      )}

      {/* Export Section */}
      {(project.status === "complete" || project.current_step >= 4) && finalPackage && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Step 4: Export Final Package</h2>

          <div className="space-y-4">
            <p className="text-green-600">✓ Pipeline complete!</p>

            <div className="bg-gray-50 rounded p-4">
              <h3 className="font-medium text-gray-900 mb-2">Package Contents:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Trend Report</li>
                <li>• {finalPackage.concepts.concepts.length} Video Concepts</li>
                <li>• Selected Concept</li>
                <li>• Full Script ({finalPackage.script.segments.length} segments)</li>
                <li>• {finalPackage.video_prompts.scene_prompts.length} Video Prompts</li>
              </ul>
            </div>

            <div className="flex gap-3">
              <button className="btn btn-primary" onClick={handleDownloadFinalPackage}>
                Download final-package.json
              </button>
              <Link href="/" className="btn btn-secondary">
                Back to Projects
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
