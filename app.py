import os
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session
import streamlit as st
from PIL import Image
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import *
import db
import cv2
from enhancer import resolution_dlss

def open_db():
    engine = create_engine("sqlite:///db.sqlite3")
    Session = sessionmaker(bind=engine)
    return Session()

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

st.set_page_config(layout='wide')
st.sidebar.header(PROJECT_NAME)
choice = st.sidebar.radio("Project menu", MENU_OPTION)


if choice == 'Upload':
    st.title('Uploading image')
    imgs = st.file_uploader("Choose a image to upload",type = ('JPG','PNG'),accept_multiple_files=True)
    st.sidebar.info("Use small images of size below 256px resolution to see best effect of dlss")
    for imgdata in imgs:
        if imgdata:
            # load image as a Pillow object
            im = Image.open(imgdata)
            # create a address for image path
            path = os.path.join(UPLOAD_FOLDER,imgdata.name)
            # save file to upload folder
            im.save(path,format=imgdata.type.split('/')[1])
            # saves info to db
            sess = open_db()
            imdb = db.Image(path=path)
            sess.add(imdb)
            sess.commit()
            sess.close()
            # show a msg
            st.success('image uploaded successfully')

if choice == 'Enhance Resolution':
    st.title('Enhance Resolution')
    
    sess = open_db()
    images = sess.query(db.Image).all()
    sess.close()
    imagepaths = [img.path for img in images ]
    with st.spinner("Please wait while DLSS works"):
        result_list = resolution_dlss("DLSS_results\model.h5")
        # st.write(result_list)
        st.success("DLSS task completed")
        for item in result_list:
            c2,c3,c4 = st.beta_columns(3)
            c2.image(item['resize128'],caption="orignal")
            c3.image(item['normal_resize_2x'],caption='normal resized')
            c4.image(item['dlss_2x'],caption='dlss')

if choice == 'Remove uploads':
    st.title('Remove uploads')   
    sess = open_db()
    images = sess.query(db.Image).all()
    sess.close()
    # show the image names in sidebar to select one
    select_img = st.radio("select an image",images)
    if select_img and st.button("remove"):
        sess = open_db()
        sess.query(db.Image).filter(db.Image.id==select_img.id).delete()
        if os.path.exists(select_img.path):
            os.unlink(select_img.path)
        sess.commit()
        sess.close()
        st.success('image removed successfully')     

if choice =='training progress':
    for file in os.listdir('training_images'):
        st.image(os.path.join('training_images',file),use_column_width=True)
if choice == 'About':
    st.title('What is the project')
    st.write('Deep learning super sampling (DLSS) is an image up scaling algorithm developed by Nvidia  using deep learning to upscale lower-resolution images to a higher-resolution for display on higher-resolution computer monitors. This technology upscale images with quality similar to that of rendering the image natively in the higher-resolution but with less computation done by the video card allowing for higher graphical settings and frame rates for a given resolution.\n In this project we will use this topic i.e. Image Resolution Enhancement using DLSS and before starting this topic I think we should discuss about what actually Image Enhancing is – It means that using this technology we can improve the quality of the image with better resolution, quality and attractive look.\n The reason behind for making this project is better resolution of the image. Now a day’s everyone has this image issue problem that if we have a passport size photo and we want that photo in bigger size and when try to make that photo bigger in resolution then the pixel of that photo gets up and down and then the result is photo got blur. So in this project we come up with the better solution. This Image Enhancer will help you to get any type of photo with any resolution without getting photo blur with a better quality.')
   
if choice == 'Creator info':
    st.title('Creators')   
    st.write('Creators are those who help to build this awesome project with a number of failures and hardwork by using number of tools and done it at the end with the full of joyness')
    st.image('suuu.jpeg', caption='Shubham Rai',width=200)
    st.image('sidit.jpg', caption='Sidit Srivastava',width=200)