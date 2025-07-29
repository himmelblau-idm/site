# Remove heading like `# AAD-TOOL("1")`
/^# [A-Z0-9_.-]+\(".*"\)/d
/^# "?[A-Z0-9_.-\\]+"?\("[0-9]+"\)/d


# Remove duplicated SYNOPSIS section
/^## SYNOPSIS$/ {
  x
  /SYNOPSIS/ d
  x
}

# Remove duplicated DESCRIPTION section
/^## DESCRIPTION$/ {
  x
  /DESCRIPTION/ d
  x
}

# Remove `_\,` artifacts
s/_\\,[[:space:]]*//g

# Remove `\/_` artifacts
s/\\\/_//g

# Fix escaped underscores like `\_`
s/\\_/_/g

# Collapse repeated blank lines
/^\s*$/N
/^\s*\n\s*$/D

# Add a newline before each bullet
/^\* /i\
\

s/"Commands:"/Commands:/g

s/\\,\\<([^>]*)>\\\//\&lt;\1\&gt;/g
s/\\<([^>]*)>/\&lt;\1\&gt;/g

s/\\,//g
s/\\\///g

# himmelblau.conf options as sections
s/^\* \*\*(.+)\*\*/#### \1/g

# Fix examples in himmelblau.conf
s/([^X])AMPLES/\1\n##### EXAMPLES\n/g

# Bold: B]textR] → **text**
s/B\]([^R]+)R\]/**\1**/g

# Manual touch ups in pam_himmelblau
s/B\]PAM\\_AUTH\\_ERRR\]/**PAM_AUTH_ERR**/g
s/B\]PAM\\_USER\\_UNKNOWNR\]/**PAM_USER_UNKNOWN**/g
s/B\]PAM\\_IGNORER\]/**PAM_IGNORE**/g
s/B\]PAM\\_SERVICE\\_ERRR\]/**PAM_SERVICE_ERR**/g
s/B\]PAM\\_CRED\\_INSUFFICIENTR\]/**PAM_CRED_INSUFFICIENT**/g
s/B\]PAM\\_ABORTR\]/**PAM_ABORT**/g

# Code: CR]textR] → `text`
s/CR\]([^R]+)R\]/`\1`/g

# Italic: I]textR] → *text*
s/I\]([^R]+)R\]/*\1*/g

# Fix escaped underscores like `\_`
s/\\_/_/g

# Bullet • 
s/ • /\n\n* /g
