"use client";

import { VideoPromptArtifact } from "@/lib/api";

interface VideoPromptViewerProps {
  videoPrompts: VideoPromptArtifact;
}

export function VideoPromptViewer({ videoPrompts }: VideoPromptViewerProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-6">
      <div className="card bg-indigo-50">
        <h2 className="text-xl font-bold text-gray-900">{videoPrompts.video_title}</h2>
        <div className="mt-2 text-sm text-gray-600">
          Style: {videoPrompts.style_direction}
        </div>
      </div>

      <div className="card">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Global Visual Rules
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-gray-400 uppercase">Aspect Ratio</div>
            <div className="font-medium">{videoPrompts.global_visual_rules.aspect_ratio}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400 uppercase">Quality</div>
            <div className="font-medium">{videoPrompts.global_visual_rules.quality_target}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400 uppercase">Frame Rate</div>
            <div className="font-medium">{videoPrompts.global_visual_rules.frame_rate}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400 uppercase">Visual Style</div>
            <div className="font-medium">{videoPrompts.global_visual_rules.visual_style}</div>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t">
          <div className="text-xs text-gray-400 uppercase">Continuity Notes</div>
          <div className="text-sm text-gray-600 mt-1">
            {videoPrompts.global_visual_rules.continuity_notes}
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          Scene Prompts ({videoPrompts.scene_prompts.length} scenes)
        </h3>

        {videoPrompts.scene_prompts.map((scene, index) => (
          <div key={scene.scene_id} className="card border-l-4 border-l-indigo-400">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="bg-indigo-100 text-indigo-700 text-xs font-mono px-2 py-1 rounded">
                  {scene.scene_id}
                </span>
                <span className="text-xs text-gray-500">
                  {formatDuration(scene.start_sec)} - {formatDuration(scene.end_sec)}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    scene.priority === "required"
                      ? "bg-red-100 text-red-700"
                      : scene.priority === "recommended"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {scene.priority}
                </span>
              </div>
              <div className="text-xs text-gray-400">
                Segment: {scene.related_segment_id}
              </div>
            </div>

            <div className="mb-3">
              <div className="text-sm font-medium text-gray-700 mb-1">
                {scene.scene_goal}
              </div>
              <div className="text-gray-600 text-sm leading-relaxed">
                {scene.prompt}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-xs text-gray-400 uppercase">Camera</div>
                <div className="text-gray-700">{scene.camera_direction}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Lighting</div>
                <div className="text-gray-700">{scene.lighting}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Action</div>
                <div className="text-gray-700">{scene.action}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Environment</div>
                <div className="text-gray-700">{scene.environment}</div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-xs text-gray-400 uppercase">Negative Prompt</div>
                <div className="text-gray-500 text-xs">{scene.negative_prompt}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Audio</div>
                <div className="text-gray-700">{scene.audio_suggestion}</div>
              </div>
            </div>

            {(scene.transition_in || scene.transition_out) && (
              <div className="mt-2 flex gap-4 text-xs">
                {scene.transition_in && (
                  <span className="text-gray-400">
                    In: {scene.transition_in}
                  </span>
                )}
                {scene.transition_out && (
                  <span className="text-gray-400">
                    Out: {scene.transition_out}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
