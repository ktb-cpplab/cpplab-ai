def makeQuery(userinfo):
    user_query = "\n".join([
        f"희망 직무: {userinfo.hopeJob}",
        f"주요 기술 스택: {', '.join(userinfo.mainStack)}",
        f"희망 회사: {', '.join(userinfo.hopeCompany)}",
        f"학력: {', '.join([f'{edu.university}({edu.department}) GPA: {edu.gpa}/{edu.gpaMax}' for edu in userinfo.educations])}",
        f"프로젝트 경험: {', '.join([proj.title for proj in userinfo.projects])}",
        f"수상 내역: {', '.join([prize.title for prize in userinfo.prizes])}",
        f"활동: {', '.join([activity.title for activity in userinfo.activities])}",
        f"보유 자격증: {', '.join([cert.certificateName for cert in userinfo.certificates])}"
    ])
    return user_query

def searchJobposting(user_query, vectorstore, k=20):
    results_with_scores = vectorstore.similarity_search_with_score(user_query, k = k)
    return results_with_scores

def convert_to_context(results_with_scores):
    job_posting = "\n\n".join(
        f"{doc.page_content}\n사용자와의 Cosine Distance: {score}"
        for doc, score in results_with_scores
    )
    return job_posting

def summarize_job_posting(userinfo, job_posting, summary_chain, k=20):
    summarized_job_posting = summary_chain.ainvoke(
        input={
            "k": k,
            "hopeJob": userinfo.hopeJob,
            "job_posting": job_posting
        }
    )
    return summarized_job_posting

def parseData(userinfo, summarized_job_posting, themes, res):
    data = {}
    data['user_portfolio'] = userinfo.model_dump()
    data['summarized_job_posting'] = summarized_job_posting
    data['theme'] = themes['themes'][0] # 프로젝트 생성에 사용된 주제
    data['project'] = res
    data['projectOptions'] = [theme for theme in themes['themes'][1:]] # 후보 프로젝트 주제들
    data['prev_theme'] = [data['theme']['title']] # 이전에 생성된 프로젝트 주제
    return data

def findTheme(data, regeninfo):
    hope_theme = None
    for i in data['projectOptions']:
        if i['title'] == regeninfo.projectOption:
            hope_theme = i
    return hope_theme

