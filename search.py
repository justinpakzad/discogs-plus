import time
# from style_genres import genres, styles, country, formats


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
        AND EXISTS (
            SELECT 1
            FROM unnest(%s) AS s
            WHERE filtered_drd.style LIKE s
        )
        {one_release_condition}
        {no_master_condition}
    ORDER BY filtered_drd.artist_name, filtered_drd.release_year, r.title, filtered_drd.country
    {limit_clause}
    """

    cursor.execute(q, (genre, formatz, year_from, year_to, countries, style))
    results = cursor.fetchall()
    tracks = [{'release_id': release_id, 'artist': artist, 'title': title, 'label': label, 'year': release_year, 'country': country,'video':video} for
              release_id, artist, title, label, release_year, country,video in results]
    return tracks


# def validate_input(g, s, c, f):
#     valid_genre = genres
#     valid_styles = styles
#     valid_countries = country
#     valid_format  = formats

#     if g  != 'Electronic':
#         return False

#     if ',' in s:
#         s_list = s.split(',')
#         for styl in s_list:
#             if styl not in valid_styles:
#                 return False
#     elif s not in valid_styles:
#             return False

#     if ',' in c:
#         c_list = c.split(',')
#         for ct in c_list:
#             if ct not in valid_countries:
#                 return False
#     elif c not in valid_countries:
#         return False

#     if ',' in f:
#         f_list = f.split(',')
#         for form in f_list:
#             if form not in valid_format:
#                 return False
#     elif f not in valid_format:
#         return False
#     return True
