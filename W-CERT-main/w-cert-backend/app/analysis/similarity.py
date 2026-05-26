"""
W-CERT Heuristic Similarity Scorer (RAG Retrieval Engine)
Provides lightweight, dependency-free similarity scoring between incidents.
"""

def find_similar_cases(target_desc, target_attack_type, target_tags, all_incidents, target_id=None, limit=3):
    """
    Finds the most similar past incidents based on a heuristic scoring model.
    Only considers closed or escalated incidents for historical context.
    
    Args:
        target_desc (str): The description of the new incident.
        target_attack_type (str): The attack type of the new incident.
        target_tags (list): List of detected tags for the new incident.
        all_incidents (list): List of all incident dictionaries from the database.
        target_id (str): The ID of the current incident (to exclude it from results).
        limit (int): Number of top results to return.
        
    Returns:
        list: Top `limit` similar incidents with a 'similarity_score' and 'match_reason' added.
    """
    scored_cases = []
    
    # Normalize inputs
    t_tags = set([t.lower().strip() for t in target_tags]) if target_tags else set()
    t_words = set(target_desc.lower().split()) if target_desc else set()
    
    for inc in all_incidents:
        # Skip the incident itself
        if target_id and inc.get('incident_id') == target_id:
            continue
            
        # Only learn from cases that are resolved/escalated/closed
        status = inc.get('status', 'OPEN')
        if status not in ['ESCALATED', 'CLOSED', 'RESOLVED']:
            continue
            
        score = 0
        reasons = []
        
        # 1. Attack Type Match (Highest Weight: 40 pts)
        if inc.get('attack_type') == target_attack_type and target_attack_type != 'Unknown':
            score += 40
            reasons.append(f"Same category ({target_attack_type})")
            
        # 2. Tag Intersection Match (Medium Weight: up to 35 pts)
        inc_tags_raw = inc.get('detected_tags', '')
        if isinstance(inc_tags_raw, str):
            i_tags = set([t.lower().strip() for t in inc_tags_raw.split(',') if t.strip()])
        else:
            i_tags = set([t.lower().strip() for t in (inc_tags_raw or [])])
            
        if t_tags and i_tags:
            overlap = t_tags.intersection(i_tags)
            if overlap:
                # Up to 35 points depending on overlap ratio
                tag_score = min(35, len(overlap) * 15)
                score += tag_score
                reasons.append(f"Shared tags ({', '.join(list(overlap)[:2])})")
                
        # 3. Keyword Overlap in Description (Low Weight: up to 25 pts)
        inc_desc = inc.get('description', '').lower()
        i_words = set(inc_desc.split())
        
        # Filter out common stop words roughly
        stop_words = {'the', 'and', 'a', 'to', 'of', 'in', 'i', 'is', 'that', 'it', 'on', 'you', 'this', 'for', 'my', 'me', 'with'}
        t_words_clean = t_words - stop_words
        i_words_clean = i_words - stop_words
        
        if t_words_clean and i_words_clean:
            word_overlap = t_words_clean.intersection(i_words_clean)
            if len(word_overlap) > 3:
                # 2 points per common word, max 25
                word_score = min(25, len(word_overlap) * 2)
                score += word_score
                if "Shared keywords" not in reasons:
                    reasons.append("Similar description context")
                    
        # Only include if there is meaningful similarity (> 20)
        if score > 20:
            # Create a safe copy of the incident for frontend/RAG
            safe_inc = {
                'incident_id': inc.get('incident_id'),
                'attack_type': inc.get('attack_type', 'Unknown'),
                'severity': inc.get('severity', 'LOW'),
                'status': status,
                'description': inc.get('description', ''),
                'similarity_score': score,
                'match_reason': ' + '.join(reasons)
            }
            scored_cases.append(safe_inc)
            
    # Sort descending by score
    scored_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return scored_cases[:limit]
