import face_recognition
import numpy as np
from PIL import Image
import io
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from uuid import UUID

from src.app.database.db import AsyncSession
from src.app.database.models import User


class FaceRecognitionService:
    def __init__(self, session: AsyncSession):
        self.session = session
            
    async def register_face_for_current_user(
            self,
            user: User,
            file: UploadFile
    ):
        contents = await file.read()

        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image, dtype=np.uint8)

        encodings = face_recognition.face_encodings(image)

        if not encodings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Face not detected."
            )

        if len(encodings) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Exactly one face required."
            )
        
        encoding = encodings[0]

        encoding_bytes = encoding.tobytes()

        user.face_encoding = encoding_bytes

        await self.session.commit()

        return {"message": "Face saved successfully"}


    async def recognize_user_by_face(
            self,
            file: UploadFile
    ):
        contents = await file.read()

        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image, dtype=np.uint8)

        encodings = face_recognition.face_encodings(image)

        if not encodings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Face not detected."
            )

        if len(encodings) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Exactly one face required."
            )
        
        input_encoding = encodings[0]

        result = await self.session.execute(
            select(User).where(User.face_encoding.is_not(None))
        )
        users = result.scalars().all()

        for user in users:
            db_encoding = np.frombuffer(user.face_encoding, dtype=np.float64)

            distance = face_recognition.face_distance([db_encoding], input_encoding)[0]
            
            if distance < 0.5:
                return {
                    "user_id": str(user.id),
                    "email": user.email
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Face not recognized."
        )
    
    async def delete_face_from_db(
            self,
            user: User,
            user_id: UUID | None = None
    ):
        target_user_id = user.id or user_id

        result = await self.session.execute(
            select(User).where(User.id == target_user_id)
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found."
            )
        
        user.face_encoding = None

        await self.session.commit()

        return {"detail": "Photo deleted."}




    
    
    
    

