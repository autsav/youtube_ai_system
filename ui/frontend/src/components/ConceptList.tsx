"use client";

import { useState } from "react";
import { VideoConcept } from "@/lib/api";

interface ConceptListProps {
  concepts: VideoConcept[];
  onSelect: (conceptId: string) => void;
  loading?: boolean;
}

export function ConceptList({ concepts, onSelect, loading }: ConceptListProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (conceptId: string) => {
    setSelectedId(conceptId);
  };

  const handleConfirm = () => {
    if (selectedId) {
      onSelect(selectedId);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4">
        {concepts.map((concept, index) => (
          <div
            key={concept.concept_id}
            className={`card cursor-pointer transition-all ${
              selectedId === concept.concept_id
                ? "border-blue-500 ring-2 ring-blue-200"
                : "hover:border-gray-300"
            }`}
            onClick={() => handleSelect(concept.concept_id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2 py-1 rounded">
                    #{index + 1}
                  </span>
                  <span className="bg-blue-100 text-blue-600 text-xs font-medium px-2 py-1 rounded uppercase">
                    {concept.format}
                  </span>
                </div>

                <h4 className="font-semibold text-gray-900 mb-1">
                  {concept.title_options[0]}
                </h4>

                <p className="text-sm text-gray-600 mb-3">{concept.premise}</p>

                <div className="text-sm text-gray-500 space-y-1">
                  <div>
                    <span className="font-medium">Hook:</span> {concept.hook_script}
                  </div>
                  <div className="flex gap-4 mt-2">
                    <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
                      CTR: {concept.predicted_ctr_range}
                    </span>
                    <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
                      AVD: {concept.predicted_avd_range}
                    </span>
                  </div>
                </div>

                {concept.title_options.length > 1 && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="text-xs text-gray-500 mb-1">Alternative titles:</div>
                    <div className="text-sm text-gray-600">
                      {concept.title_options.slice(1).join(" • ")}
                    </div>
                  </div>
                )}
              </div>

              <div className="ml-4">
                <div
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    selectedId === concept.concept_id
                      ? "border-blue-500 bg-blue-500"
                      : "border-gray-300"
                  }`}
                >
                  {selectedId === concept.concept_id && (
                    <div className="w-2.5 h-2.5 bg-white rounded-full" />
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedId && (
        <div className="flex justify-end pt-4 border-t">
          <button
            className="btn btn-primary"
            onClick={handleConfirm}
            disabled={loading}
          >
            {loading ? "Selecting..." : "Select This Concept"}
          </button>
        </div>
      )}
    </div>
  );
}
