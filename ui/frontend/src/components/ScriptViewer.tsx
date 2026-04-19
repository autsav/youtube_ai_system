"use client";

import { ScriptArtifact } from "@/lib/api";

interface ScriptViewerProps {
  script: ScriptArtifact;
}

export function ScriptViewer({ script }: ScriptViewerProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-6">
      <div className="card bg-blue-50">
        <h2 className="text-xl font-bold text-gray-900">{script.video_title}</h2>
        <div className="mt-2 text-sm text-gray-600">
          Target Length: {script.target_length_min} minutes
        </div>
      </div>

      <div className="card border-l-4 border-l-purple-500">
        <h3 className="text-sm font-medium text-purple-600 uppercase tracking-wide mb-3">
          Hook ({formatDuration(script.hook.start_sec)} - {formatDuration(script.hook.end_sec)})
        </h3>
        <blockquote className="text-lg font-medium text-gray-800 italic border-l-2 border-gray-300 pl-4">
          "{script.hook.spoken_words}"
        </blockquote>
        <div className="mt-2 text-sm text-gray-500">Type: {script.hook.hook_type}</div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          Segments
        </h3>

        {script.segments.map((segment, index) => (
          <div
            key={segment.segment_id}
            className={`card border-l-4 ${
              segment.segment_id === "seg_01"
                ? "border-l-blue-500"
                : index === script.segments.length - 1
                ? "border-l-green-500"
                : "border-l-gray-300"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                    {segment.segment_id}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDuration(segment.start_sec)} - {formatDuration(segment.end_sec)}
                  </span>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      segment.drop_risk === "low"
                        ? "bg-green-100 text-green-700"
                        : segment.drop_risk === "medium"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {segment.drop_risk} risk
                  </span>
                </div>

                <div className="text-sm font-medium text-gray-900 mb-1">
                  {segment.purpose}
                </div>

                <div className="text-gray-700 mb-2">{segment.spoken_script}</div>

                <div className="text-sm text-gray-500 space-y-1">
                  <div>
                    <span className="font-medium">Emotion:</span> {segment.emotion}
                  </div>
                  <div>
                    <span className="font-medium">Retention Device:</span>{" "}
                    {segment.retention_device}
                  </div>
                  <div>
                    <span className="font-medium">Why viewer stays:</span>{" "}
                    {segment.why_viewer_stays}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {script.mid_video_hooks.length > 0 && (
        <div className="card border-l-4 border-l-orange-400">
          <h3 className="text-sm font-medium text-orange-600 uppercase tracking-wide mb-3">
            Mid-Video Hooks
          </h3>
          <div className="space-y-2">
            {script.mid_video_hooks.map((hook, i) => (
              <div key={i} className="text-sm">
                <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">
                  {formatDuration(hook.time_sec)}
                </span>
                <span className="ml-2 text-gray-700">"{hook.line}"</span>
                <span className="ml-2 text-gray-400">({hook.purpose})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card border-l-4 border-l-green-500">
        <h3 className="text-sm font-medium text-green-600 uppercase tracking-wide mb-3">
          Call to Action ({formatDuration(script.cta.time_sec)})
        </h3>
        <blockquote className="text-gray-800 italic">"{script.cta.line}"</blockquote>
        <div className="mt-2 text-sm text-gray-500">Goal: {script.cta.goal}</div>
      </div>

      <div className="card bg-gray-50">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Retention Summary
        </h3>
        <div className="space-y-2 text-sm">
          <div>
            <span className="font-medium">Opening:</span>{" "}
            {script.retention_summary.opening_strategy}
          </div>
          <div>
            <span className="font-medium">Payoff:</span> {" "}
            {script.retention_summary.payoff_strategy}
          </div>
          {script.retention_summary.reengagement_points.length > 0 && (
            <div>
              <span className="font-medium">Re-engagement:</span>
              <ul className="list-disc list-inside ml-2 mt-1 text-gray-600">
                {script.retention_summary.reengagement_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
