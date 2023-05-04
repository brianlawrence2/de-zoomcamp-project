import json

from typing import Union

from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission

class RedditEncoder(json.JSONEncoder):
    def default(self, obj: Union[Comment,Submission]) -> dict:
        if isinstance(obj, Comment):
            return {
                'id': obj.id,
                'author': {
                    'id': obj.author.id,
                    'is_mod': obj.author.is_mod,
                    'name': obj.author.name,
                    'created_utc': obj.author.created_utc,
                    'comment_karma': obj.author.comment_karma,
                    'link_karma': obj.author.link_karma
                },
                'body': obj.body,
                'body_html': obj.body_html,
                'created_utc': obj.created_utc,
                'distinguished': obj.distinguished,
                'edited': obj.edited,
                'is_submitter': obj.is_submitter,
                'link_id': obj.link_id,
                'parent_id': obj.parent_id,
                'permalink': obj.permalink,
                'saved': obj.saved,
                'score': obj.score,
                'stickied': obj.stickied,
                'submission': obj.submission,
                'subreddit_id': obj.subreddit_id
            }
        
        if isinstance(obj, Submission):
            return {
                'id': obj.id,
                'author': {
                    'id': obj.author.id,
                    'is_mod': obj.author.is_mod,
                    'name': obj.author.name,
                    'created_utc': obj.author.created_utc,
                    'comment_karma': obj.author.comment_karma,
                    'link_karma': obj.author.link_karma
                },
                'author_flair_text': obj.author_flair_text,
                'clicked': obj.clicked,
                'created_utc': obj.created_utc,
                'distinguished': obj.distinguished,
                'edited': obj.edited,
                'is_original_content': obj.is_original_content,
                'is_self': obj.is_self,
                'link_flair_template_id': obj.link_flair_template_id,
                'link_flair_text': obj.link_flair_text,
                'locked': obj.locked,
                'name': obj.fullname,
                'num_comments': obj.num_comments,
                'over_18': obj.over_18,
                'permalink': obj.permalink,
                'poll_data': obj.poll_data if hasattr(obj, 'poll_data') else None,
                'saved': obj.saved,
                'score': obj.score,
                'selftext': obj.selftext,
                'spoiler': obj.spoiler,
                'stickied': obj.stickied,
                'title': obj.title,
                'upvote_raito': obj.upvote_ratio,
                'url': obj.url
            }

        return super().default(obj)