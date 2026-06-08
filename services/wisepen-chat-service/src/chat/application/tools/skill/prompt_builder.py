from typing import Any

from chat.domain.entities.skill import SkillMeta


class SkillPromptBuilder:
    @staticmethod
    def build_available_skills_prompt(skills: list[SkillMeta]) -> str:
        skill_lines = [
            f"- id=\"{skill.skill_id}\" name=\"{skill.display_name}\": {skill.description}"
            for skill in skills
        ]
        return (
            "[Available WisePen Skills]\n"
            "The following skills are available in this turn as lightweight metadata. "
            "Each skill contains detailed domain instructions in SKILL.md and may include supporting assets.\n"
            "Strict rules:\n"
            "1. If the user explicitly asks to use one of the listed skills by id or name, call `load_skill` for that skill.\n"
            "2. Otherwise, call `load_skill` only when a listed skill is directly useful for the current request. Do not load speculatively.\n"
            "3. To load a skill, call `load_skill` with `skill_id` exactly as listed below.\n"
            "4. After loading, the returned SKILL.md is mandatory for the current task. Follow its Scope, Output Format, and Constraints precisely.\n"
            "5. Call `load_skill_asset` only after loading a skill, and only if the loaded SKILL.md explicitly requires a listed asset.\n"
            "6. If none of the skills apply, ignore this list and answer normally.\n\n"
            "Skills:\n"
            + "\n".join(skill_lines)
        )

    @staticmethod
    def build_skill_output_placeholder(tool_call_arguments: dict[str, Any], output: Any) -> str:
        skill_id = tool_call_arguments.get("skill_id") or "unknown"
        return (
            "[Skill content omitted from persistent history. "
            f"skill_id={skill_id}. "
            "If this skill is needed again after summarization or in a later turn, call load_skill with this skill_id.]"
        )

    @staticmethod
    def build_skill_asset_output_placeholder(tool_call_arguments: dict[str, Any], output: Any) -> str:
        skill_id = tool_call_arguments.get("skill_id") or "unknown"
        path = tool_call_arguments.get("path") or "unknown"
        return (
            "[Skill asset content omitted from persistent history. "
            f"skill_id={skill_id} path={path}. "
            "If this asset is needed again after summarization or in a later turn, reload the skill and call load_skill_asset.]"
        )
