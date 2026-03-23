import face_recognition
import numpy as np
from PIL import Image
import io
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from uuid import UUID

from src.app.database.db import AsyncSession
from src.app.database.models import User
from src.app.repositories.user_repository import UserRepository


class FaceRecognitionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)
            
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

        users = await self.user_repo.get_user_with_face_encode()

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
            user: User | None = None,
            user_id: UUID | None = None
    ):
        existing_user = await self.user_repo.get_user(user_id=user_id)
        
        if not user:
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User not found."
                )
            
            existing_user.face_encoding = None

            await self.session.commit()

            return {"detail": f"User with ID: {user_id} Photo deleted."}
        
        if not user_id:    
            existing_user.face_encoding = None

            await self.session.commit()

            return {"detail": "Photo deleted."}



        




    
    
    
    

