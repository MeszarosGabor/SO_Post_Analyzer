class PostBlock:
    def __init__(self, post_id):
        self.post_id = post_id
        self.content = ""

    def is_empty(self):
        return not self.content.strip()

    def append(self, line):
        if self.content:
            self.content += "\n" + line
        else:
            self.content = line

    def prepend(self, content):
        if self.content:
            self.content = content + "\n" + self.content
        else:
            self.content = content


class CodeBlock(PostBlock):
    pass


class TextBlock(PostBlock):
    pass


# TABLE HEADERS
POSTS_COLS = [
    "PostTypeId",
    "AcceptedAnswerId",
    "CreationDate",
    "Score",
    "ViewCount",
    "Body",
    "OwnerUserId",
    "LastActivityDate",
    "Tags",
    "CommentCount",
    "AnswerCount",
    "ParentId",
]

LANGUAGES = {
    "c",
    "c++",
    "c#",
    "python",
    "ruby",
    "rust",
    "java",
    "javascript",
    "julia",
    "r",
    "perl",
    "php",
    "matlab",
    "objective-c",
    "swift",
}
