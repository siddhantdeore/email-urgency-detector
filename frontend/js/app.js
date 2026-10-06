/**
 * Cognitive Email Urgency Detector - Interactive Frontend Application
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analyze-form");
  const subjectInput = document.getElementById("email-subject");
  const bodyInput = document.getElementById("email-body");
  const senderInput = document.getElementById("email-sender");
  const senderRoleInput = document.getElementById("email-role");
  const departmentInput = document.getElementById("email-department");
  const btnAnalyze = document.getElementById("btn-analyze");
  const resultsContainer = document.getElementById("results-container");
  const examplesContainer = document.getElementById("examples-chips");
  const feedbackContainer = document.getElementById("feedback-container");

  // Load Preloaded Examples
  loadExamples();

  // Form Submit Handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = subjectInput.value.trim();
    const body = bodyInput.value.trim();

    if (!subject && !body) {
      alert("Please provide an email subject or body to analyze.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject,
          body,
          sender: senderInput.value.trim() || null,
          sender_role: senderRoleInput.value.trim() || null,
          department: departmentInput.value.trim() || null
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Analysis request failed.");
      }

      const data = await response.json();
      renderResults(data, subject, body);
    } catch (err) {
      alert(`Error analyzing email: ${err.message}`);
    } finally {
      setLoading(false);
    }
  });

  async function loadExamples() {
    try {
      const res = await fetch("/api/examples");
      if (res.ok) {
        const examples = await res.json();
        renderExampleChips(examples);
      }
    } catch (e) {
      console.warn("Could not fetch remote examples:", e);
    }
  }

  function renderExampleChips(examples) {
    if (!examplesContainer) return;
    examplesContainer.innerHTML = "";

    examples.forEach((ex) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "example-chip";

      // Tag class based on title
      let tagClass = "medium";
      if (ex.title.includes("Critical")) tagClass = "critical";
      else if (ex.title.includes("High")) tagClass = "high";
      else if (ex.title.includes("Low")) tagClass = "low";

      chip.innerHTML = `
        <span class="chip-tag ${tagClass}">${tagClass}</span>
        <span>${escapeHtml(ex.title)}</span>
      `;

      chip.addEventListener("click", () => {
        subjectInput.value = ex.subject;
        bodyInput.value = ex.body;
        if (senderInput) senderInput.value = ex.sender || "";
        if (senderRoleInput) senderRoleInput.value = ex.sender_role || "";
        
        // Scroll to form and highlight
        subjectInput.focus();
        form.scrollIntoView({ behavior: "smooth", block: "center" });
      });

      examplesContainer.appendChild(chip);
    });
  }

  function setLoading(isLoading) {
    if (isLoading) {
      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = `<span class="spinner"></span> Performing Cognitive Analysis...`;
    } else {
      btnAnalyze.disabled = false;
      btnAnalyze.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 6v6l4 2"></path>
        </svg>
        Analyze Email
      `;
    }
  }

  function renderResults(data, subject, body) {
    resultsContainer.style.display = "block";
    resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });

    // 1. Urgency Badge & Score Container Theme
    const headerCard = document.getElementById("res-header-card");
    headerCard.className = `result-header-card ${data.urgency_level}`;

    const urgencyBadge = document.getElementById("res-urgency-badge");
    urgencyBadge.className = `urgency-badge ${data.urgency_level}`;
    urgencyBadge.textContent = data.urgency_level.toUpperCase();

    // 2. Score & Confidence
    animateScore(data.urgency_score);
    document.getElementById("res-confidence").textContent = `${Math.round(data.confidence * 100)}%`;
    document.getElementById("res-intent").textContent = data.intent;
    document.getElementById("res-intent-conf").textContent = `${Math.round(data.intent_confidence * 100)}%`;

    // 3. Temporal & Business Impact
    document.getElementById("res-temporal").textContent = data.temporal_constraint || "None detected";
    document.getElementById("res-business").textContent = data.business_impact;

    // 4. Immediate Human Attention Banner
    const attentionBanner = document.getElementById("res-attention-banner");
    if (data.requires_immediate_attention) {
      attentionBanner.className = "action-banner critical-action";
      attentionBanner.innerHTML = `
        <h4>Triage Protocol: Immediate Human Attention Required</h4>
        <p>⚠️ High-stakes urgency detected. Immediate escalation and active human intervention required.</p>
      `;
    } else {
      attentionBanner.className = "action-banner";
      attentionBanner.innerHTML = `
        <h4>Triage Protocol: Standard Processing</h4>
        <p>✓ Normal workflow queue. No emergency escalation required.</p>
      `;
    }

    // 5. Recommended Action
    document.getElementById("res-action-text").textContent = data.recommended_action;

    // 6. Cognitive Factor Breakdown Bars
    updateProgressBar("prog-ml", data.cognitive_breakdown.ml_prediction);
    updateProgressBar("prog-temp", data.cognitive_breakdown.temporal_urgency);
    updateProgressBar("prog-biz", data.cognitive_breakdown.business_impact);
    updateProgressBar("prog-lang", data.cognitive_breakdown.urgency_language);
    updateProgressBar("prog-sev", data.cognitive_breakdown.context_severity);

    // 7. Reasoning Narrative & Bullet Points
    document.getElementById("res-detailed-explanation").innerHTML = formatMarkdown(data.detailed_explanation);

    const reasonsList = document.getElementById("res-reasons-list");
    reasonsList.innerHTML = "";
    data.reasoning.forEach((reason) => {
      const li = document.createElement("li");
      li.className = "reasoning-item";
      li.textContent = reason;
      reasonsList.appendChild(li);
    });

    // 8. Highlighted Email Body Preview
    const previewBox = document.getElementById("res-email-preview");
    previewBox.innerHTML = data.highlighted_html;

    // 9. Feedback Component
    renderFeedbackWidget(data, subject, body);
  }

  function updateProgressBar(id, value) {
    const valElement = document.getElementById(`${id}-val`);
    const barElement = document.getElementById(`${id}-bar`);
    if (valElement) valElement.textContent = `${Math.round(value)}%`;
    if (barElement) barElement.style.width = `${Math.min(100, Math.max(0, value))}%`;
  }

  function animateScore(targetScore) {
    const el = document.getElementById("res-score-num");
    let current = 0;
    const duration = 800;
    const stepTime = 15;
    const stepVal = targetScore / (duration / stepTime);

    const timer = setInterval(() => {
      current += stepVal;
      if (current >= targetScore) {
        current = targetScore;
        clearInterval(timer);
      }
      el.textContent = Math.round(current);
    }, stepTime);
  }

  function renderFeedbackWidget(data, subject, body) {
    if (!feedbackContainer) return;
    feedbackContainer.innerHTML = `
      <div class="feedback-box">
        <div>
          <strong>Was this priority decision accurate?</strong>
          <span style="font-size: 0.8rem; color: var(--text-muted); display: block;">Your feedback trains the adaptive cognitive model.</span>
        </div>
        <div class="feedback-btns" id="fb-action-btns">
          <button type="button" class="btn-sm" id="btn-fb-yes">👍 Yes, Accurate</button>
          <button type="button" class="btn-sm" id="btn-fb-no">👎 No, Correct</button>
        </div>
      </div>
      <div id="fb-correction-panel" style="display: none; margin-top: 0.75rem; background: var(--bg-card); padding: 1rem; border-radius: var(--radius-sm);">
        <label class="form-label">Select Correct Urgency Level:</label>
        <select class="form-control" id="fb-corrected-level" style="margin-bottom: 0.5rem;">
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        <button type="button" class="btn-sm" id="btn-submit-correction" style="background: var(--primary);">Submit Correction</button>
      </div>
    `;

    document.getElementById("btn-fb-yes").addEventListener("click", () => {
      submitFeedback(subject, body, data.urgency_level, data.urgency_level, "Confirmed accurate by user");
    });

    document.getElementById("btn-fb-no").addEventListener("click", () => {
      document.getElementById("fb-correction-panel").style.display = "block";
    });

    document.getElementById("btn-submit-correction").addEventListener("click", () => {
      const corrected = document.getElementById("fb-corrected-level").value;
      submitFeedback(subject, body, data.urgency_level, corrected, "User corrected urgency");
    });
  }

  async function submitFeedback(subject, body, predicted, actual, comments) {
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject,
          body,
          predicted_urgency: predicted,
          actual_urgency: actual,
          comments
        })
      });
      if (res.ok) {
        feedbackContainer.innerHTML = `
          <div style="color: var(--low); font-size: 0.9rem; padding: 0.75rem; background: var(--low-bg); border-radius: var(--radius-sm);">
            ✓ Feedback saved successfully! This will inform future model adaptation cycles.
          </div>
        `;
      }
    } catch (e) {
      alert("Failed to submit feedback.");
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatMarkdown(text) {
    if (!text) return "";
    return text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  }
});

