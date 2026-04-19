"use client";

import { useState } from "react";
import { ChannelBrief } from "@/lib/api";

interface BriefFormProps {
  onSubmit: (name: string, brief: ChannelBrief) => void;
  loading?: boolean;
}

export function BriefForm({ onSubmit, loading }: BriefFormProps) {
  const [name, setName] = useState("");
  const [brief, setBrief] = useState<ChannelBrief>({
    channel_name: "",
    niche: "",
    target_audience: "",
    tone: "",
    target_length_min: 10,
    brand_colors: [],
    format_preferences: [],
    visual_style: "",
    cta_goal: "",
    asset_preferences: {
      stock_sites: ["Artgrid"],
      ai_video_tool: "Kling 3.0",
      editor: "Premiere Pro",
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(name, brief);
  };

  const updateField = <K extends keyof ChannelBrief>(key: K, value: ChannelBrief[K]) => {
    setBrief((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="label">Project Name *</label>
        <input
          type="text"
          className="input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="My YouTube Project"
          required
        />
      </div>

      <div className="border-t pt-6">
        <h3 className="text-lg font-medium mb-4">Channel Brief</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">Channel Name *</label>
            <input
              type="text"
              className="input"
              value={brief.channel_name}
              onChange={(e) => updateField("channel_name", e.target.value)}
              placeholder="Creator Systems Lab"
              required
            />
          </div>

          <div>
            <label className="label">Niche *</label>
            <input
              type="text"
              className="input"
              value={brief.niche}
              onChange={(e) => updateField("niche", e.target.value)}
              placeholder="AI tools"
              required
            />
          </div>

          <div>
            <label className="label">Target Audience *</label>
            <input
              type="text"
              className="input"
              value={brief.target_audience}
              onChange={(e) => updateField("target_audience", e.target.value)}
              placeholder="tech-savvy freelancers"
              required
            />
          </div>

          <div>
            <label className="label">Tone *</label>
            <input
              type="text"
              className="input"
              value={brief.tone}
              onChange={(e) => updateField("tone", e.target.value)}
              placeholder="high-energy but analytical"
              required
            />
          </div>

          <div>
            <label className="label">Target Length (min) *</label>
            <input
              type="number"
              className="input"
              min={1}
              max={180}
              value={brief.target_length_min}
              onChange={(e) => updateField("target_length_min", parseInt(e.target.value) || 10)}
              required
            />
          </div>

          <div>
            <label className="label">Visual Style *</label>
            <input
              type="text"
              className="input"
              value={brief.visual_style}
              onChange={(e) => updateField("visual_style", e.target.value)}
              placeholder="cinematic tech documentary"
              required
            />
          </div>

          <div>
            <label className="label">CTA Goal *</label>
            <input
              type="text"
              className="input"
              value={brief.cta_goal}
              onChange={(e) => updateField("cta_goal", e.target.value)}
              placeholder="Subscribe and watch the next workflow breakdown."
              required
            />
          </div>

          <div>
            <label className="label">Brand Colors (comma-separated)</label>
            <input
              type="text"
              className="input"
              value={brief.brand_colors.join(", ")}
              onChange={(e) =>
                updateField(
                  "brand_colors",
                  e.target.value.split(",").map((c) => c.trim()).filter(Boolean)
                )
              }
              placeholder="#00FF66, #000000"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Creating..." : "Create Project"}
        </button>
      </div>
    </form>
  );
}
