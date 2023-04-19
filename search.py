from validate import styles, country, formats
import os

def search_tracks(conn, genre, search_format, style, year_from, year_to, countries, one_release=False, no_master=False, limit_results=False):
    cursor = conn.cursor()
    style = ['%' + s.strip() + '%' for s in style.split(',')] if style else ['%']
    countries = [c.strip() for c in countries.split(',')] if countries else ['%']
    formatz = [f.strip() for f in search_format.split(',')]  if search_format else ['%']

    limit_clause = "LIMIT 120" if limit_results else ""

    one_release_condition = f"AND filtered_drd.artist_release_count = 1" if one_release else ""

    no_master_condition = f"AND r.master_id IS NULL" if no_master else ""

    q = f"""
    WITH filtered_drd AS (
        SELECT *,
            COUNT(*) OVER (PARTITION BY artist_name) as artist_release_count
        FROM trimmed_denormalized_release_data
        WHERE
            genre = %s
            AND format LIKE ANY(%s)
            AND release_year BETWEEN %s AND %s
            AND country LIKE ANY(%s)
    )
    SELECT DISTINCT ON (filtered_drd.artist_name)
        r.id as release_id,
        filtered_drd.artist_name,
        r.title,
        filtered_drd.label_name,
        filtered_drd.release_year,
        filtered_drd.country,
        rv.uri
    FROM
        release_trimmed r
    JOIN release_video_trimmed AS rv ON r.id = rv.release_id
    JOIN release_artist_trimmed ra ON r.id = ra.release_id
    JOIN filtered_drd ON r.title = filtered_drd.title AND ra.artist_name = filtered_drd.artist_name
    WHERE
        ra.role = ''
        AND filtered_drd.style LIKE ANY(ARRAY(SELECT '%' || s || '%' FROM unnest(%s::TEXT[]) AS s))
        {one_release_condition}
        {no_master_condition}
    ORDER BY filtered_drd.artist_name, filtered_drd.release_year, r.title, filtered_drd.country
    {limit_clause}
    LIMIT 25
    """
    cursor.execute(q, (genre, formatz, year_from, year_to, countries, style))
    results = cursor.fetchall()
    tracks = [{'release_id': release_id, 'artist': artist, 'title': title, 'label': label, 'year': release_year, 'country': country,'video':video} for
              release_id, artist, title, label, release_year, country,video in results]
    return tracks


def validate_input(g, s, c, f):
    valid_styles = styles
    valid_countries = country
    valid_format  = formats

    if g  != 'Electronic':
        return False

    if ',' in s:
        s_list = s.split(',')
        for styl in s_list:
            if styl not in valid_styles:
                return False
    elif s not in valid_styles:
            return False

    if ',' in c:
        c_list = c.split(',')
        for ct in c_list:
            if ct not in valid_countries:
                return False
    elif c not in valid_countries:
        return False

    if ',' in f:
        f_list = f.split(',')
        for form in f_list:
            if form not in valid_format:
                return False
    elif f not in valid_format:
        return False
    return True









# def get_filtered_data(cur, genre, search_format, release_year_start, release_year_end, countries, style, one_release=False):

#     one_release_condition = f"AND artist_release_count = 1" if one_release else ""
#     style = ['%' + s.strip() + '%' for s in style.split(',')] if style else ['%']
#     formatz = [f.strip() for f in search_format.split(',')]  if search_format else ['%']
#     countries = [c.strip() for c in countries.split(',')] if countries else ['%']
#     query = f"""
#         SELECT *,
#             COUNT(*) OVER (PARTITION BY artist_name) as artist_release_count
#         FROM trimmed_denormalized_release_data
#         WHERE
#             genre = %s
#             AND format LIKE ANY(%s)
#             AND release_year BETWEEN %s AND %s
#             AND country LIKE ANY(%s)
#             AND style LIKE ANY(ARRAY(SELECT '%' || s || '%' FROM unnest(%s::TEXT[]) AS s))
#             {one_release_condition}
#     """
#     cur.execute(query, (genre, formatz, release_year_start, release_year_end, countries, style))
#     return cur.fetchall()

# def get_release_data(cur, release_ids, no_master=False):
#     no_master_condition = f"AND r.master_id IS NULL" if no_master else ""

#     query = f"""
#         SELECT r.id as release_id,
#             ra.artist_name,
#             r.title,
#             ra.role
#         FROM release_trimmed r
#         JOIN release_artist_trimmed ra ON r.id = ra.release_id
#         WHERE r.id = ANY(%s)
#         AND ra.role = ''
#         {no_master_condition}
#     """

#     cur.execute(query, (release_ids,))
#     return cur.fetchall()

# def get_video_data(cur, release_ids):
#     query = """
#         SELECT r.id as release_id,
#             rv.uri
#         FROM release_trimmed r
#         JOIN release_video_trimmed rv ON r.id = rv.release_id
#         WHERE r.id = ANY(%s)
#     """

#     cur.execute(query, (release_ids,))
#     return cur.fetchall()

# def merge_and_format_results(filtered_data_results, release_data_results, video_data_results):
#     tracks = []

#     for filtered_data_row in filtered_data_results:
#         release_id = filtered_data_row[0]
#         artist_name = filtered_data_row[1]
#         title = filtered_data_row[2]
#         label_name = filtered_data_row[3]
#         release_year = filtered_data_row[4]
#         country = filtered_data_row[5]

#         matching_release_data = [row for row in release_data_results if row[0] == release_id]

#         if not matching_release_data:
#             continue

#         matching_video_data = [row for row in video_data_results if row[0] == release_id]
#         video_uri = matching_video_data[0][1] if matching_video_data else None

#         track = {
#             'release_id': release_id,
#             'artist': artist_name,
#             'title': title,
#             'label': label_name,
#             'year': release_year,
#             'country': country,
#             'video': video_uri
#         }
#         tracks.append(track)

#     return tracks

# connection = create_cloud_connection()
# cur = connection.cursor()

# filtered_data_results = get_filtered_data(cur, 'Electronic', 'CD', 1990, 1991, 'US', 'Techno')
# print(filtered_data_results)
# release_ids = [row[0] for row in filtered_data_results]

# release_data_results = get_release_data(cur, release_ids)

# video_data_results = get_video_data(cur, release_ids)

# cur.close()
# connection.close()

# tracks = merge_and_format_results(filtered_data_results, release_data_results, video_data_results)
# tracks = tracks[:10]
