TABLE_JOIN_SCOREPROJ = "(SELECT proj_id_id,teacher_id,presentation,question,report,presentation_media,discover,analysis,quantity,levels,quality\
            FROM database_management_scoreproj\
            INNER JOIN database_management_teacher_score_projs\
            ON database_management_scoreproj.ID = database_management_teacher_score_projs.scoreproj_id\
            INNER JOIN database_management_teacher\
            ON database_management_teacher_score_projs.teacher_id = database_management_teacher.ID\
            ) join_data_score_proj"

TABLE_JOIN_SCOREPOST = "(SELECT proj_id_id,teacher_id,time_spo,character_spo,presentation_spo,question_spo,media_spo,quality_spo \
            FROM database_management_scoreposter\
			INNER JOIN database_management_teacher_score_posters\
            ON database_management_scoreposter.ID = database_management_teacher_score_posters.scoreposter_id\
            INNER JOIN database_management_teacher\
            ON database_management_teacher_score_posters.teacher_id = database_management_teacher.ID) join_data_score_poster "

CONDITION_RESULT = "WHERE join_data_score_proj.teacher_id = join_data_score_poster.teacher_id\
            GROUP BY join_data_score_proj.teacher_id ,join_data_score_poster.teacher_id"

JOIN_MEAN_SCORE = "SELECT  AVG(join_data_score_proj.quality) as quality_proj,\
        (AVG(presentation)+AVG(question)+AVG(report)+AVG(presentation_media)+AVG(discover)+AVG(analysis)+AVG(quantity)+AVG(levels))/8 as RESULT_score_proj,\
        (AVG(time_spo)+AVG(character_spo)+AVG(presentation_spo)+AVG(question_spo)+AVG(media_spo)+AVG(quality_spo))/6 as RESULT_score_poster\
        FROM "+TABLE_JOIN_SCOREPROJ+", "+TABLE_JOIN_SCOREPOST+CONDITION_RESULT

TEACHER_JOIN = "SELECT join_data_score_proj.teacher_id FROM"+TABLE_JOIN_SCOREPROJ+", "+TABLE_JOIN_SCOREPOST+CONDITION_RESULT

LEVELS_TEACHER = "SELECT id,levels_teacher FROM database_management_teacher\
            WHERE id in ("+TEACHER_JOIN+")"
