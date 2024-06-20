from pydantic import BaseModel

from quizzing.quiz.domain.entities.quiz import AnswerOption, Question, Quiz


class QuizCreate(BaseModel):
    title: str


class QuizRead(BaseModel):
    id: str
    title: str
    author_id: str
    status: str
    questions: list["QuestionRead"]

    @classmethod
    def from_entity(cls, quiz: Quiz) -> "QuizRead":
        return cls(
            id=quiz.id,
            title=quiz.title,
            author_id=quiz.author_id,
            status=quiz.status.value,
            questions=[QuestionRead.from_entity(q) for q in quiz.questions],
        )


class QuestionRead(BaseModel):
    text: str
    options: list[str]
    correct_options: list[str]

    @classmethod
    def from_entity(cls, question: Question) -> "QuestionRead":
        return cls(
            text=question.text,
            options=[str(q) for q in question.options],
            correct_options=[str(q) for q in question.correct_options],
        )


class QuestionCreate(QuestionRead):
    def to_entity(self) -> Question:
        return Question(
            text=self.text,
            options=[AnswerOption(option) for option in self.options],
            correct_options={AnswerOption(option) for option in self.correct_options},
        )


class QuizUpdate(BaseModel):
    title: str
    questions: list[QuestionCreate]