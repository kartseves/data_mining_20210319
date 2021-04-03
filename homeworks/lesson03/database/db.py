
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    @staticmethod
    def _get_or_create(session, model, unique_field, unique_value, **data):
        db_data = session.query(model).filter(unique_field == unique_value).first()
        if not db_data:
            db_data = model(**data)
            session.add(db_data)
            try:
                session.commit()
            except Exception as exc:
                print(exc)
                session.rollback()
        return db_data

    def _get_or_create_comments(self, session, json_data: list) -> list:
        result = []
        if json_data:
            for comment in json_data:
                comment_writer = self._get_or_create(
                    session,
                    models.Writer,
                    models.Writer.url,
                    comment["comment"]["user"]["url"],
                    name=comment["comment"]["user"]["full_name"],
                    url=comment["comment"]["user"]["url"],
                )
                db_comment = self._get_or_create(
                    session,
                    models.Comment,
                    models.Comment.id,
                    comment["comment"]["id"],
                    **comment["comment"],
                    writer=comment_writer,
                )

                result.append(db_comment)
                result.extend(
                    self._get_or_create_comments(session, comment["comment"]["children"])
                )

        return result

    def create_post(self, data):
        session = self.maker()
        writer = self._get_or_create(
            session,
            models.Writer,
            models.Writer.url,
            data["writer_data"]["url"],
            **data["writer_data"],
        )
        tags = map(
            lambda tag_data: self._get_or_create(
                session, models.Tag, models.Tag.url, tag_data["url"], **tag_data
            ),
            data["tags_data"],
        )
        post = self._get_or_create(
            session,
            models.Post,
            models.Post.gb_id,
            data["post_data"]["gb_id"],
            **data["post_data"],
            writer=writer,
        )

        comments = self._get_or_create_comments(session, data["comments_data"])

        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
